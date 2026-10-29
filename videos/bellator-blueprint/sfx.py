# Banda sonora sintetizada (solo numpy): drone, trazos, whooshes en cortes, subida del escaneo e impacto final.
# Salida: out/audio.wav (48 kHz, estéreo). Los tiempos siguen el montaje de index.html.
import numpy as np, wave

SR = 48000
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))

def env(n, a, r, curve=2.0):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na) ** curve
    e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e

def bandnoise(dur, f0, f1, bw=0.5):
    """Ruido filtrado con banda móvil f0->f1 (overlap-add por bloques FFT)."""
    n = int(dur * SR); hop = 1024; win = 2048
    x = rng.standard_normal(n + win); y = np.zeros(n + win); w = np.hanning(win)
    fr = np.fft.rfftfreq(win, 1 / SR)
    for k, i in enumerate(range(0, n, hop)):
        p = i / max(1, n); fc = f0 * (f1 / f0) ** p
        g = np.exp(-0.5 * (np.log2(np.maximum(fr, 1) / fc) / bw) ** 2)
        y[i:i + win] += np.fft.irfft(np.fft.rfft(x[i:i + win] * w) * g) * w
    y = y[:n]; return y / (np.abs(y).max() + 1e-9)

def tone(dur, f, harm=(1,), decay=None):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * h * t) / (k + 1) for k, h in enumerate(harm))
    if decay: s *= np.exp(-t / decay)
    return s

def whoosh(dur=0.7, up=True):
    s = bandnoise(dur, 300 if up else 3000, 3000 if up else 300, 0.6)
    e = np.sin(np.linspace(0, np.pi, len(s))) ** 1.5
    return s * e

def hit(f=48, dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    fm = f * (1 + 1.6 * np.exp(-t / 0.05))
    body = np.sin(2 * np.pi * np.cumsum(fm) / SR) * np.exp(-t / 0.45)
    click = bandnoise(0.06, 2500, 1200, 0.8) * np.exp(-np.arange(int(0.06 * SR)) / SR / 0.012)
    body[: len(click)] += click * 0.5
    return body

def tick():
    n = int(0.03 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.004)

# 1) drone de fondo (La): pad que se abre en la transición y cambia de color en la parte real
t = np.arange(N) / SR
pad = np.zeros(N)
for f, a in [(55, .5), (110, .35), (164.8, .18), (220, .12), (261.6, .08)]:
    pad += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (1 + 0.15 * np.sin(2 * np.pi * 0.11 * t + f))
open_ = np.clip((t - 7.3) / 2.5, 0, 1)
shimmer = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(440, .05), (659.3, .035), (880, .02)]) * open_
pad = (pad + shimmer) * np.clip(t / 1.2, 0, 1)
pad *= np.where(t < 14.6, 1.0, np.clip(1 - (t - 14.6) / 0.4, 0.35, 1))  # bajada al entrar el hero
pad *= np.clip((DUR - t) / 1.6, 0, 1)
L += pad * 0.22; R += pad * 0.22

# 2) textura de "lápiz" durante el blueprint (ruido agudo muy suave)
pen = bandnoise(7.2, 5000, 6500, 0.4) * 0.05 * env(int(7.2 * SR), 0.4, 0.5)
add(pen, 0.0, 1.0, -0.2)
# ticks de cotas/etiquetas
for tt in [0.45, 1.75, 2.25, 3.2, 3.7, 4.75, 6.25, 6.55]:
    add(tick(), tt, 0.25, 0.4)
# 3) whooshes en cada corte (como el montaje de referencia)
for tt, up, pan in [(1.53, True, -.3), (2.9, False, .3), (4.37, True, -.3), (7.25, False, .3),
                    (11.55, True, -.4), (13.05, False, .4)]:
    w = whoosh(0.7, up); add(w, tt - 0.45, 0.32, pan)
# destello del plano del mango
add(hit(70, 0.9), 5.8, 0.35); add(whoosh(0.5, True), 5.45, 0.3)
# 4) subida del escaneo (blueprint -> realidad)
rs = bandnoise(2.2, 400, 6000, 0.35) * np.linspace(0, 1, int(2.2 * SR)) ** 2
add(rs, 7.35, 0.28)
riser = tone(2.6, 1, (1,)) * 0
tt_ = np.arange(int(2.6 * SR)) / SR
add(np.sin(2 * np.pi * np.cumsum(220 * 2 ** (tt_ / 2.6)) / SR) * (tt_ / 2.6) ** 2 * 0.5, 7.4, 0.12)
# 5) entrada a la pala real y macros
add(hit(45, 1.8), 10.0, 0.75); add(whoosh(0.6, False), 9.7, 0.35)
for tt in [11.55, 13.05]:
    add(hit(60, 0.7), tt, 0.32)
# 6) hero: golpe grave, brillo con el barrido de luz y acorde final
add(hit(40, 2.4), 14.6, 0.9); add(whoosh(0.9, False), 14.15, 0.35)
sw = bandnoise(1.4, 2000, 9000, 0.5) * np.sin(np.linspace(0, np.pi, int(1.4 * SR))) ** 2
add(sw, 16.2, 0.12, -0.5)
add(hit(50, 2.0), 18.0, 0.55)
ch = sum(tone(2.2, f, (1, 2), decay=1.2) * a for f, a in [(220, .5), (277.2, .35), (329.6, .35), (440, .2)])
add(ch * env(len(ch), 0.02, 1.0), 18.0, 0.18)

# mezcla: fundido final, normalización a pico -1 dBFS
fade = np.clip((DUR - t) / 0.6, 0, 1); L *= fade; R *= fade
m = max(np.abs(L).max(), np.abs(R).max()); g = 10 ** (-1 / 20) / m
st = (np.stack([L, R], 1) * g * 32767).astype(np.int16)
with wave.open('out/audio.wav', 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(st.tobytes())
print('ok', st.shape)
