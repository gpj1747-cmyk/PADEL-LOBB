# Banda sonora sintetizada, estilo tráiler épico (numpy + scipy):
# braams, sub-drops, golpes tipo taiko, whooshes, riser con pulsos que aceleran y reverb larga.
# Salida: out/audio.wav (48 kHz, estéreo). Los tiempos siguen el montaje de index.html.
import numpy as np, wave
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
H0 = 10.0            # inicio del hero (igual que en index.html)
DUR = H0 + 5.4
N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)          # bus seco
RL = np.zeros(N); RR = np.zeros(N)        # envío a reverb

def add(sig, t0, gain=1.0, pan=0.0, rev=0.3):
    i = int(t0 * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    if j <= i: return
    s = sig[: j - i] * gain
    gl, gr = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    L[i:j] += s * gl; R[i:j] += s * gr
    RL[i:j] += s * gl * rev; RR[i:j] += s * gr * rev

def T(d): return np.arange(int(d * SR)) / SR
def lp(x, f, o=4): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=4): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def norm(x): return x / (np.abs(x).max() + 1e-9)

def sweep_noise(d, f0, f1, bw=0.6):
    """Ruido con banda que se desplaza f0->f1 (bloques solapados)."""
    n = int(d * SR); hop, win = 512, 2048
    x = rng.standard_normal(n + win); y = np.zeros(n + win); w = np.hanning(win)
    fr = np.fft.rfftfreq(win, 1 / SR)
    for i in range(0, n, hop):
        fc = f0 * (f1 / f0) ** (i / max(1, n))
        g = np.exp(-0.5 * (np.log2(np.maximum(fr, 1) / fc) / bw) ** 2)
        y[i:i + win] += np.fft.irfft(np.fft.rfft(x[i:i + win] * w) * g) * w
    return norm(y[:n])

def whoosh(d=0.8, up=True, bright=1.0):
    s = sweep_noise(d, 250 if up else 4500 * bright, 4500 * bright if up else 250, 0.7)
    e = np.sin(np.linspace(0, np.pi, len(s))) ** 2
    if up: e *= np.linspace(0.4, 1, len(s))
    return s * e

def reverse_swell(d=1.2, f=2000):
    s = lp(rng.standard_normal(int(d * SR)), f)
    t = T(d); return norm(s) * (t / d) ** 3

def sub_drop(d=2.0, f0=90, f1=28):
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t / 0.35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (d * 0.45))

def taiko(d=1.4, f=58):
    t = T(d); fm = f * (1 + 0.9 * np.exp(-t / 0.03))
    body = np.sin(2 * np.pi * np.cumsum(fm) / SR) * np.exp(-t / 0.35)
    skin = lp(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.05) * 0.6
    crack = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.008) * 0.25
    return norm(np.tanh(1.8 * (body + skin + crack)))

def impact(d=2.5, f=45):
    t = T(d)
    s = taiko(d, f) * 0.9 + sub_drop(d, 120, f * 0.6) * 0.8
    metal = sum(np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) for fr in [523, 811, 1249, 1903]) * np.exp(-t / 0.6) * 0.06
    return norm(np.tanh(1.5 * (s + metal)))

def braam(d=3.0, root=55.0, open_t=0.25):
    """Metales graves distorsionados (sierra desafinada + quinta + octava) con filtro que se abre."""
    t = T(d); s = np.zeros(len(t))
    for mul, a in [(1, 1), (1.5, .55), (2, .5), (0.5, .7)]:
        for det in (-0.12, 0.0, 0.13):
            f = root * mul * 2 ** (det / 12)
            ph = (f * t + rng.uniform()) % 1
            s += a * (2 * ph - 1)
    s = np.tanh(0.6 * s)
    # filtro que se abre y se cierra, por bloques
    out = np.zeros(len(s)); blk = 2048
    for i in range(0, len(s), blk):
        tt = i / SR
        fc = 180 + 2600 * min(1, tt / open_t) * np.exp(-max(0, tt - open_t) / (d * 0.35))
        out[i:i + blk] = lp(s[max(0, i - 4096): i + blk], fc, 2)[-len(s[i:i + blk]):]
    env = np.minimum(1, t / 0.04) * np.exp(-t / (d * 0.5))
    return norm(out * env)

def tick():
    t = T(0.05)
    return (np.sin(2 * np.pi * 2800 * t) * np.exp(-t / 0.006) + hp(rng.standard_normal(len(t)), 6000) * np.exp(-t / 0.003) * 0.5)

def glitch(d=0.18):
    t = T(d); s = np.sign(np.sin(2 * np.pi * 180 * t * (1 + 6 * t))) * (rng.random(len(t)) > 0.3)
    return hp(s.astype(float), 400) * np.exp(-t / 0.08)

t = T(DUR)

# 1) Fondo: drone grave + pulso tipo latido que crece durante el blueprint
dr = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f, a in [(36.7, .6), (55, .5), (73.4, .25), (110, .12)])
dr *= (1 + 0.2 * np.sin(2 * np.pi * 0.2 * t))
dr *= np.clip(t / 0.8, 0, 1) * np.where(t < H0, 1, 0.25) * np.clip((DUR - t) / 2.0, 0, 1)
hi = lp(rng.standard_normal(N), 9000); hi = hp(hi, 5000) * 0.012 * np.clip((t - 0.3) / 1, 0, 1) * (t < 7.4)   # "lápiz"
L += dr * 0.22 + hi; R += dr * 0.22 + hi
beat = 60 / 76
for k in range(int(7.2 / beat)):
    tb = 0.6 + k * beat
    g = 0.25 + 0.35 * (tb / 7.2)
    add(lp(taiko(0.6, 50), 400), tb, g, 0, 0.15)
    add(lp(taiko(0.4, 46), 300), tb + 0.22, g * 0.55, 0, 0.1)

# 2) Arranque: golpe + subida inversa al primer fotograma
add(impact(2.2, 42), 0.0, 0.7, 0, 0.5)
add(sweep_noise(1.6, 6000, 9000, 0.4) * np.exp(-T(1.6) / 0.5), 0.0, 0.15, 0.3, 0.6)

# 3) Cortes del blueprint: whoosh + golpe tipo taiko
cuts = [(1.53, -0.4), (2.9, 0.4), (4.37, -0.4), (7.25, 0.4)]
for i, (tc, pan) in enumerate(cuts):
    add(whoosh(0.7, i % 2 == 0), tc - 0.5, 0.55, pan, 0.35)
    add(taiko(1.4, 62 - i * 3), tc, 0.75, 0, 0.45)
# destello del mango: braam corto + impacto
add(reverse_swell(0.9, 3000), 5.8 - 0.9, 0.5, 0, 0.2)
add(impact(2.4, 44), 5.8, 0.95, 0, 0.6)
add(braam(1.6, 55, 0.12), 5.8, 0.5, 0, 0.5)
# etiquetas: ticks digitales y pequeños glitches
for tc in [0.45, 1.75, 2.25, 3.2, 3.7, 4.75, 6.25, 6.55]:
    add(tick(), tc, 0.35, 0.5, 0.2); add(glitch(), tc + 0.05, 0.12, -0.5, 0.1)

# 4) Escaneo (blueprint -> realidad): riser largo con pulsos que aceleran y tono que sube
rd = H0 - 7.3
rs = sweep_noise(rd, 300, 9000, 0.5) * (T(rd) / rd) ** 2
add(rs, 7.3, 0.55, 0, 0.4)
tr = T(rd); f = 110 * 2 ** (2 * tr / rd)
saw = sum(((fm * np.cumsum(f) / SR + rng.uniform()) % 1) * 2 - 1 for fm in (1, 1.006, 2.01))
add(lp(np.tanh(saw), 3000) * (tr / rd) ** 2.5, 7.3, 0.25, 0, 0.4)
k = 0.0; tp = 7.4
while tp < H0 - 0.12:                    # pulsos cada vez más rápidos
    add(taiko(0.35, 70), tp, 0.25 + 0.4 * (tp - 7.4) / rd, 0, 0.15)
    tp += max(0.07, 0.42 * (1 - (tp - 7.4) / rd) ** 1.6)
add(reverse_swell(1.0, 5000), H0 - 1.0, 0.6, 0, 0.3)

# 5) Revelación del hero: silencio de un instante y BRAAM + sub-drop + impacto
add(impact(3.5, 38), H0 + 0.02, 1.0, 0, 0.8)
add(braam(4.5, 55, 0.3), H0 + 0.02, 0.85, 0, 0.7)
add(braam(4.5, 41.2, 0.4), H0 + 0.02, 0.45, 0, 0.7)
add(sub_drop(3.0, 70, 24), H0 + 0.02, 0.9, 0, 0.2)
add(whoosh(1.2, False, 1.3), H0 + 0.1, 0.3, 0.6, 0.6)
# barrido de luz: brillo metálico
sh = sweep_noise(1.4, 3000, 12000, 0.4) * np.sin(np.linspace(0, np.pi, int(1.4 * SR))) ** 2
add(sh, H0 + 1.6, 0.22, -0.6, 0.8)
tt = T(2.0)
bell = sum(np.sin(2 * np.pi * fr * tt) * a for fr, a in [(880, .5), (1320, .3), (1760, .2), (2637, .1)]) * np.exp(-tt / 0.7)
add(bell, H0 + 2.2, 0.12, 0.5, 0.9)
# 6) Títulos: golpe final + braam + acorde con cola larga
add(reverse_swell(0.8, 4000), H0 + 3.4 - 0.8, 0.45, 0, 0.3)
add(impact(3.0, 40), H0 + 3.4, 0.95, 0, 0.9)
add(braam(2.0, 55, 0.08), H0 + 3.4, 0.6, 0, 0.8)
tt = T(2.0)
ch = sum(np.sin(2 * np.pi * fr * tt) * a for fr, a in [(110, .5), (164.8, .4), (220, .35), (261.6, .25), (329.6, .2)]) * np.exp(-tt / 1.1)
add(ch * np.minimum(1, tt / 0.03), H0 + 3.4, 0.3, 0, 0.9)

# reverb: respuesta impulsional de ruido con caída de ~3 s (estéreo decorrelado)
ir_t = T(3.2)
irL = lp(rng.standard_normal(len(ir_t)), 7000) * np.exp(-ir_t / 0.75)
irR = lp(rng.standard_normal(len(ir_t)), 7000) * np.exp(-ir_t / 0.75)
wl = fftconvolve(RL, irL)[:N]; wr = fftconvolve(RR, irR)[:N]
sc = np.abs(np.r_[L, R]).max() / (np.abs(np.r_[wl, wr]).max() + 1e-9)
L2 = L + wl * sc * 0.35; R2 = R + wr * sc * 0.35

# master: compresión suave (tanh), fundido final, pico -1 dBFS
fade = np.clip((DUR - t) / 0.5, 0, 1)
L2 = np.tanh(1.4 * L2 / np.abs(L2).max()) * fade; R2 = np.tanh(1.4 * R2 / np.abs(R2).max()) * fade
m = max(np.abs(L2).max(), np.abs(R2).max()); g = 10 ** (-1 / 20) / m
st = (np.stack([L2, R2], 1) * g * 32767).astype(np.int16)
with wave.open('out/audio.wav', 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(st.tobytes())
print('ok', DUR)
