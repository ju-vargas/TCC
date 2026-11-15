"""Parte de cada etapa no recurso e na potência dinâmica, tudo do Vivado 2023.2 do servidor (projeto roteado).

Recursos: util_hierarquica.rpt (report_utilization -hierarchical, hardware/etapas/servidor/).
Potência: report_power by hierarchy. Antes de 2026-11-14 os recursos vinham do csynth do HLS (função hls).

Etapas: LU; D e F (extração de D, D^1/2 e F); substituição direta; inversão; restante
(memórias entre etapas, leitura/gravação, controle). Restante = total - soma das etapas.
Saída: etapas_dominantes.csv nesta pasta.
"""
import csv, glob, os, re

H = '/home/juliana/GitHub/TCC/hardware'
REL = f'{H}/relatorios_hls'
SRV = f'{H}/resultados_servidor'
FORMATOS = ['18-8', '18-8-TRN-SAT', '20-8', '22-12', '24-12', '26-12', '28-14', '30-14']
# sem_otimizacao_32x32: só HLS (síntese C local 2026.1, 2026-11-14); sem potência por pedido da autora.
ARQS = {'sem_otimizacao': 'TDLA30-5', 'sem_otimizacao_32x32': None, '9090': 'TDLA30-5', '4545': 'TDLA30-10', '606': 'TDLA30-75',
        '455': 'TDLC300-100', '152_sistolico': 'TDLA30-300', '114_sistolico': 'TDLB100-400'}
ETAPAS = ['lu', 'df', 'fs', 'inv']


def etapa(nome):
    if re.search(r'LU_decomposition|lote_lu|etapa_lu', nome): return 'lu'
    if re.search(r'forward_substitution|lote_fs|etapa_fs', nome): return 'fs'
    if re.search(r'inversion|lote_inv|etapa_inv', nome): return 'inv'
    if re.search(r'etapa_g|lote_g|cholesky_inverse_(Outline|Pipeline)_VITIS|cdiv|G_decomposition|sqrt_fixed|D_extraction|D_square_root', nome): return 'df'
    return None


def hls(fmt, arq):
    t = open(f'{REL}/{fmt}_{arq}/report/cholesky_inverse_csynth.rpt').read()
    t = t.split('== Utilization Estimates')[-1]
    tot = re.search(r'\|Total\s*\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|', t).groups()
    tot = dict(zip(['bram', 'dsp', 'ff', 'lut'], map(int, tot)))
    sec = re.search(r'\* Instance:\s*\n(.*?)\n\s*\n', t, re.S).group(1)
    soma = {e: dict(bram=0, dsp=0, ff=0, lut=0) for e in ETAPAS}
    for l in sec.splitlines():
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if len(c) < 6 or not c[2].isdigit(): continue
        e = etapa(c[0] + ' ' + c[1])
        if e:
            for k, v in zip(['bram', 'dsp', 'ff', 'lut'], c[2:6]): soma[e][k] += int(v)
    return tot, soma


def rpt_potencia(fmt, arq):
    cen = ARQS[arq]
    if cen is None: return None
    pad = [f'{SRV}/formatos*/versoes/{fmt}_{arq}/trabalho/potencia/potencia_{cen}.rpt']
    if fmt == '24-12' and arq in ('152_sistolico', '114_sistolico'):
        pad.append(f'{SRV}/versoes/{arq}/trabalho/potencia/potencia_{cen}.rpt')
        pad.append(f'{SRV}/versoes/{arq}/**/potencia_{cen}.rpt')
    for p in pad:
        g = sorted(glob.glob(p, recursive=True))
        if g: return g[0]
    return None


def rpt_util(fmt, arq):
    pad = [f'{SRV}/formatos*/versoes/{fmt}_{arq}/trabalho/vivado/util_hierarquica.rpt']
    if fmt == '24-12' and arq in ('152_sistolico', '114_sistolico'):
        pad.append(f'{SRV}/versoes/{arq}/trabalho/vivado/util_hierarquica.rpt')
    for p in pad:
        g = sorted(glob.glob(p))
        if g: return g[0]
    return None


def vivado(fmt, arq):
    """Recursos por etapa do projeto roteado. BRAM em blocos de 18 Kb (RAMB36 = 2)."""
    f = rpt_util(fmt, arq)
    if not f: return None, None
    tot = None; soma = {e: dict(bram=0, dsp=0, ff=0, lut=0) for e in ETAPAS}
    for l in open(f):
        m = re.match(r'\|( +)(\S+)\s*\|\s*(\S+)\s*\|(.*)', l)
        if not m: continue
        c = [x.strip() for x in m.group(4).strip().strip('|').split('|')]
        if len(c) < 9 or not c[0].isdigit(): continue
        v = dict(lut=int(c[0]), ff=int(c[4]), bram=2 * int(c[5]) + int(c[6]), dsp=int(c[8]))
        nivel = len(m.group(1))
        if nivel == 1 and m.group(2) == 'cholesky_inverse': tot = v
        elif nivel == 3:
            e = etapa(m.group(2) + ' ' + m.group(3))
            if e:
                for k in v: soma[e][k] += v[k]
    return tot, soma


def potencia(fmt, arq):
    f = rpt_potencia(fmt, arq)
    if not f: return None, None
    t = open(f).read()
    bloco = t.split('3.1 By Hierarchy')[2]
    tot = None; soma = {e: 0.0 for e in ETAPAS}
    for l in bloco.splitlines():
        m = re.match(r'\|( +)(\S+)\s*\|\s*([\d.]+)\s*\|', l)
        if not m: continue
        nivel = len(m.group(1))
        if nivel == 1 and m.group(2) == 'cholesky_inverse': tot = float(m.group(3))
        elif nivel == 3:
            e = etapa(m.group(2))
            if e: soma[e] += float(m.group(3))
    return tot, soma


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'etapas_dominantes.csv')
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['formato', 'arquitetura', 'grandeza', 'total'] + ETAPAS + ['restante', 'fonte'])
        for arq in ARQS:
            for fmt in FORMATOS:
                tot, soma = vivado(fmt, arq)
                if tot is None:
                    print('sem util_hierarquica:', fmt, arq); continue
                for k in ['lut', 'ff', 'dsp', 'bram']:
                    s = [soma[e][k] for e in ETAPAS]
                    w.writerow([fmt, arq, k, tot[k]] + s + [tot[k] - sum(s), os.path.relpath(rpt_util(fmt, arq), H)])
                pt, ps = potencia(fmt, arq)
                if pt is not None:
                    s = [round(ps[e], 3) for e in ETAPAS]
                    w.writerow([fmt, arq, 'pdin_w', pt] + s + [round(pt - sum(s), 3), os.path.relpath(rpt_potencia(fmt, arq), H)])
    print(out)
