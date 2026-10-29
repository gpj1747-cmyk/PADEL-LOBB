# No puedes controlar todo lo que ocurre en pista (parte de texto)

Segunda parte del reel (solo texto), en 9:16 (1080×1920, 30 fps) y 11,7 s, con la canción `assets/musica.mp3`. Cada cambio cae en un golpe de la música (~161 BPM, golpes detectados con librosa).

- Tipografía: solo **Unbounded** (los 8 pesos de `fonts/`). En la parte final se varían el peso, las mayúsculas y el espaciado, sin usar otras tipografías.
- Colores: #e7350d, #898b8d y #ffffff.
- Logo: `assets/logo_padel_lobb.png` sin modificar (solo se escala de forma proporcional). El fondo del cierre usa el color exacto del PNG para que no se vea el borde.

| Tiempo | Texto |
|---|---|
| 0,0–2,1 | no puedes / **controlar** / **todo** / lo que pasa / **en pista** |
| 2,1–3,8 | ni el **resultado** / ni el **error** / ni a tu **compañero** / ni a tu **rival** |
| 3,8–5,2 | cuanto más / lo intentas / más **tensión** / **acumulas** |
| 5,2–7,1 | la clave: / **diferenciar** / lo que depende / **de ti** |
| 7,1–8,6 | actitud · atención · decisiones · respuesta (cambiando de peso cada medio golpe) |
| 8,6–10,2 | entrena / **tu mente** · y aprende / dónde poner / **tu energía** |
| 10,2–11,7 | Logo de Padel Lobb |

## Archivos
- `index.html`: la animación (`render(t)`). Si lo abres en el navegador se ve en bucle; haz clic para que suene la música.
- `render.js`: `node render.js frames` genera `out/video_mudo.mp4`, y `node render.js sheet 1 2 3` saca fotogramas sueltos.
- Montaje: `ffmpeg -i out/video_mudo.mp4 -i assets/musica.mp3 -c:v copy -c:a aac -b:a 192k -shortest no_puedes_controlar.mp4`
