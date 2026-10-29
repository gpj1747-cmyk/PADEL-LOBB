# Bellator — From Blueprint to Reality

Vídeo publicitario de 15,4 s (versión 2), en formato 4:5 (1080×1350, 30 fps), igual que el vídeo de referencia de NOX. Muestra la pala **Bellator de Padel Lobb**: empieza como plano técnico (blueprint) y termina con la pala real.

## Cómo se garantiza la fidelidad a la pala
- **No se usa IA generativa de imagen ni de vídeo.** Cada píxel de la pala que aparece en el vídeo sale de las fotos originales (`src/1.png` a `src/4.jpg`).
- Las líneas del blueprint se **extraen de la propia foto de producto** (`extract.py`): silueta, 61 agujeros, 9 manchas doradas con el corazón interior, contorno de la cara, puente, hueco triangular, mango y letras BELLATOR. El círculo de construcción se ajusta al arco real de la cabeza y el eje de simetría pasa por el centro medido.
- La foto queda alineada píxel a píxel bajo el dibujo. Por eso el paso de blueprint a realidad es un **revelado por máscara**, sin morphing ni deformación.
- Las cotas y etiquetas **no llevan cifras**: no se inventan medidas ni especificaciones.
- Los movimientos de cámara son paneos, zooms y giros 2D leves sobre fotos reales. No hay rotaciones 3D que obliguen a inventar caras de la pala que no salen en las fotos.

## Montaje (calcado al ritmo de cortes de la referencia: ~1,4 s por plano)
| Tiempo | Plano |
|---|---|
| 0,0–1,5 | FIG. 01: la cámara sigue el trazo del contorno real de la cabeza, con el círculo de construcción |
| 1,5–2,9 | FIG. 02: eje de simetría, letras BELLATOR y cota de anchura máxima |
| 2,9–4,4 | FIG. 03: patrón de agujeros y manchas doradas |
| 4,4–5,8 | FIG. 04: puente / corazón con líneas de construcción del triángulo |
| 5,8–7,25 | (destello) FIG. 05: mango y longitud del grip |
| 7,25–10,0 | FIG. 06: la línea de escaneo revela la foto real, el blueprint desaparece y el fondo pasa a estudio oscuro |
| 10,0–15,4 | Corte a negro y hero: la pala completa (recorte de la foto de producto) sobre fondo oscuro, con barrido de luz; «BELLATOR / PADEL LOBB» al final |

V2: se quitan los planos sacados de las fotos de ambiente (eran solo referencia). En `index.html`, `M0`/`H0` dejan preparado el hueco para insertar planos detalle en vídeo antes del hero (`MS`).

## Archivos
- `index.html`: la animación entera. `render(t)` es una función pura del tiempo. Ábrelo en un navegador para verlo en bucle.
- `render.js`: renderiza con Playwright → `out/video_mudo.mp4`. Con `node render.js sheet 1 2 3` saca fotogramas clave.
- `extract.py`, `seg*.py`: recorte de la pala y extracción de la geometría → `assets/`.
- `sfx.py`: banda sonora sintetizada estilo tráiler (latido de percusión grave, whooshes + golpes tipo taiko en cada corte, riser con pulsos que aceleran en el escaneo, braam + sub-drop en la revelación, golpe final con acorde y reverb larga) → `out/audio.wav`.
- Montaje final: `ffmpeg -i out/video_mudo.mp4 -i out/audio.wav -c:v copy -c:a aac -b:a 192k -shortest bellator_blueprint.mp4`

## Puntos a validar
- **Resolución de la foto de producto:** `src/1.png` es de 800×1200 y la pala ocupa unos 380 px de ancho. Los planos de revelado (7–10 s) y el hero se ven algo blandos al ampliarse. Con un packshot en alta resolución (4000 px o más, mismo encuadre) bastaría con sustituirlo y volver a ejecutar los scripts.
- Pendiente: insertar los planos detalle en vídeo de la marca (mejor calidad y más cercanos al lenguaje de la referencia).
- Las etiquetas técnicas están en inglés (como el lema «From blueprint to reality») y el texto final es «BELLATOR · PADEL LOBB» en Inter. Si la marca tiene tipografía propia, conviene usarla.
- El audio es sintético y no se ha podido escuchar.
