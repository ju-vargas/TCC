"""The HLS hardware as the M_c x M_c inverter of the BCD-MMSE update.

Each format (int bits, frac bits, quantization, overflow) and matrix size has its own
server executable: the hardware sources of TCC/hardware/cholesky_hardware/ with the
testbench TCC/hardware/cholesky_hardware_servidor/tb_servidor.cpp, compiled by the
Vitis C-simulation (compilar_servidor.sh, cached in that folder's build/). The server
stays open for the whole run: the simulator sends each ``den`` in float64 through a
pipe, the hardware converts it with ``fixed_t(double)``, inverts it and sends back the
raw registers of the inverse, which become ``raw * 2^-F``.

The rest of the simulator is float64, so above 53 bits the low bits of a register are
lost in that conversion (the hardware result itself is exact).

A division by zero kills the server, as it kills the C-simulation. The inversion then
returns NaN (the convention of `hw_inverse.cholesky_hw_inverse`), the server is
restarted, and `stats` counts it. The inverter consumes no random numbers, so a run
stays paired with the float reference.
"""

from __future__ import annotations

import os
import select
import subprocess
from collections import OrderedDict
from pathlib import Path

import numpy as np

#: TCC/hardware/cholesky_hardware_servidor, from TCC/software/simulador/dbp_sim/
SERVER_DIR = Path(os.environ.get(
    "HLS_SERVIDOR_DIR",
    Path(__file__).resolve().parents[3] / "hardware" / "cholesky_hardware_servidor"))

#: Counters since the last `reset_stats()`.
stats = {"calls": 0, "hls_calls": 0, "failed_calls": 0, "timeouts": 0, "restarts": 0}

#: The same den is rebuilt in every BCD iteration; the last few are remembered.
CACHE_SIZE = 64


def reset_stats() -> None:
    for key in stats:
        stats[key] = 0


def build(int_bits: int, frac_bits: int, quant: str, overflow: str, n: int) -> Path:
    """Folder with the server for this format and size (compiled once, then cached)."""
    folder = SERVER_DIR / "build" / f"{int_bits}_{frac_bits}_{quant}_{overflow}_{n}"
    if not (folder / "csim.exe").exists():
        subprocess.run([str(SERVER_DIR / "compilar_servidor.sh"), str(int_bits),
                        str(frac_bits), quant, overflow, str(n)],
                       check=True, stdout=subprocess.DEVNULL)
    return folder


def _no_core_dump():
    """A division by zero kills the server; without this the system writes a core dump
    each time, which takes seconds (rodar_inversoes.sh does the same with ulimit -c 0)."""
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


class _Server:
    """One open hardware process for one format and size."""

    def __init__(self, folder: Path, n: int, frac_bits: int, timeout_s: float):
        self.folder, self.n, self.timeout_s = folder, n, timeout_s
        self.scale = 2.0 ** -frac_bits
        self.env = {**os.environ,
                    "LD_LIBRARY_PATH": (folder / "ld_library_path").read_text().strip()}
        self.proc = None
        self.cache: OrderedDict[bytes, np.ndarray] = OrderedDict()

    def _start(self):
        self.proc = subprocess.Popen([str(self.folder / "csim.exe")], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                     env=self.env, bufsize=0, preexec_fn=_no_core_dump)

    def _stop(self):
        if self.proc is not None:
            self.proc.kill()
            self.proc.wait()
            self.proc = None

    def _read(self, size: int) -> bytes:
        """Exactly `size` bytes from the server, or EOFError if it dies, or TimeoutError."""
        fd = self.proc.stdout.fileno()
        data = b""
        while len(data) < size:
            ready, _, _ = select.select([fd], [], [], self.timeout_s)
            if not ready:
                raise TimeoutError
            chunk = os.read(fd, size - len(data))
            if not chunk:
                raise EOFError
            data += chunk
        return data

    def invert(self, A: np.ndarray) -> np.ndarray:
        A = np.ascontiguousarray(A, dtype=np.complex128)
        key = A.tobytes()
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        stats["hls_calls"] += 1
        if self.proc is None or self.proc.poll() is not None:
            self._start()
        try:
            self.proc.stdin.write(np.int32(self.n).tobytes() + A.view(np.float64).tobytes())
            self.proc.stdin.flush()
            status = self._read(1)[0]
            if status == 1:            # the hardware divided by zero and exited
                raise EOFError
            if status != 0:
                raise RuntimeError(f"server status {status}")
            raw = np.frombuffer(self._read(16 * self.n * self.n), dtype="<i8")
            inv = (raw[0::2] * self.scale + 1j * raw[1::2] * self.scale).reshape(self.n, self.n)
        except (BrokenPipeError, EOFError, TimeoutError) as err:
            # The hardware divided by zero, died or hung: same result as cholesky_hw_inverse
            stats["failed_calls"] += 1
            if isinstance(err, TimeoutError):
                stats["timeouts"] += 1
            stats["restarts"] += 1
            self._stop()
            inv = np.full((self.n, self.n), np.nan, dtype=complex)
        self.cache[key] = inv
        if len(self.cache) > CACHE_SIZE:
            self.cache.popitem(last=False)
        return inv


#: Open servers, kept across equalizer builds: {(format, n): _Server}
_servers: dict[tuple, _Server] = {}


def make_hls_inverter(int_bits: int, frac_bits: int, quant: str, overflow: str,
                      timeout_s: float = 60.0):
    """Inverse for the BCD-MMSE update computed by the HLS hardware in this format."""
    fmt = (int_bits, frac_bits, quant, overflow)

    def inverse(A: np.ndarray) -> np.ndarray:
        stats["calls"] += 1
        n = A.shape[0]
        server = _servers.get(fmt + (n,))
        if server is None:
            server = _Server(build(*fmt, n), n, frac_bits, timeout_s)
            _servers[fmt + (n,)] = server
        return server.invert(A)
    inverse.hls_format = fmt
    return inverse


def close_all() -> None:
    for server in _servers.values():
        server._stop()
    _servers.clear()
