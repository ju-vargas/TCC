#!/usr/bin/env python3
"""Script to download the latest QuaDRiGa and generate new channel .mat files."""

import os
import sys
import subprocess
from pathlib import Path

def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        return False
    return True

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    quadriga_dir = base_dir / "QuaDRiGa_latest"
    repo_url = "https://github.com/fraunhoferhhi/QuaDRiGa.git"
    
    # Step 1: Clone or update QuaDRiGa repo
    if not quadriga_dir.exists():
        print(f"Cloning {repo_url} into {quadriga_dir}...")
        if not run_cmd(["git", "clone", repo_url, str(quadriga_dir)]):
            sys.exit(1)
    else:
        print(f"Updating QuaDRiGa in {quadriga_dir}...")
        run_cmd(["git", "pull"], cwd=str(quadriga_dir))
    
    # Step 2: Generate temporary MATLAB script to use the new QuaDRiGa path
    matlab_dir = base_dir / "TCC" / "massive_mimo_dbp"
    if not matlab_dir.exists():
        # Fallback to current parent directory if TCC structure isn't perfect
        matlab_dir = Path(__file__).resolve().parent.parent

    print(f"Using MATLAB directory: {matlab_dir}")
    
    quadriga_src_path = quadriga_dir / "quadriga_src"
    
    tmp_m_script = matlab_dir / "update_channels_tmp.m"
    script_content = f"""
% Auto-generated script to update channels with latest QuaDRiGa
try
    disp('Adding QuaDRiGa to path...');
    addpath(genpath('{quadriga_src_path}'));
    
    disp('Running export_quadriga_channels...');
    % Set to a smaller number for quick testing or full 100 for production
    export_quadriga_channels;
    
    disp('Success! Channels exported.');
    exit(0);
catch e
    disp(getReport(e));
    exit(1);
end
"""
    tmp_m_script.write_text(script_content)
    
    # Step 3: Run MATLAB
    print("\nStarting MATLAB to generate channels (this may take a while)...")
    cmd = [
        "matlab",
        "-nodisplay",
        "-nodesktop",
        "-r",
        "run('update_channels_tmp.m')"
    ]
    
    success = run_cmd(cmd, cwd=str(matlab_dir))
    
    if tmp_m_script.exists():
        tmp_m_script.unlink()
        
    if success:
        print("\nSuccessfully updated QuaDRiGa channels!")
        print("You can now run the Python simulation to see the improved results:")
        print("  python3 main.py fig8a --channel mat_file --mat_file ../channels_fig8a_M128_C8_K8.mat")
    else:
        print("\nFailed to run MATLAB. Please check the license server or MATLAB installation.")
        print("Note: If you have a License Manager Error -15, you must run this script from an environment with a valid license.")

if __name__ == "__main__":
    main()
