// Uso: node render.js frames  -> MP4 (out/video_mudo.mp4)
//      node render.js sheet t1 t2 ...  -> hoja de contactos de fotogramas clave
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const mode = process.argv[2] || 'frames';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve('index.html') + '#manual');
  await p.evaluate(async () => { for (const w of [200,300,400,500,600,700,800,900]) await document.fonts.load(w + ' 50px U', 'añ'); await document.fonts.ready; if (!logo.complete) await new Promise(r => logo.onload = r); });
  await p.waitForTimeout(500);
  fs.mkdirSync('out', { recursive: true });
  if (mode === 'sheet') {
    const ts = process.argv.slice(3).map(Number);
    for (const t of ts) {
      await p.evaluate(t => render(t), t);
      await p.screenshot({ path: `out/k_${t.toFixed(2)}.png` });
    }
  } else {
    const dur = await p.evaluate(() => DUR), n = Math.round(dur * 30);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', 'out/video_mudo.mp4']);
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => render(t), i / 30);
      const buf = await p.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log('frame', i, '/', n);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();
