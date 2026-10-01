// Write the raster exports of the mark into mark/png from the SVGs tools/build.py writes:
//
//     npm install && npm run export
//
// Every size is a whole number of pixels to the unit, since the chapter scales the mark "by
// whole units": the square, which holds the clear space on its 24 units, at 2 to 32 pixels a
// unit, and the mark alone, for a favicon, at 1 and 2, its 16 by 14 centred on a square.
// Transparent, one file per ground, as the chapter never puts the mark on a photograph and a
// client knows its own ground.
const fs = require("fs");
const path = require("path");
const { chromium } = require("@playwright/test");

const root = path.resolve(__dirname, "..");
const out = path.join(root, "mark", "png");

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const shots = [];
  for (const ground of ["light", "dark"]) {
    for (const perUnit of [2, 4, 8, 16, 32]) {
      const side = 24 * perUnit;
      shots.push({ file: `mark-square-${ground}-${side}.png`, svg: `mark-square-${ground}.svg`, side, width: side, height: side });
    }
    for (const perUnit of [1, 2]) {
      const side = 16 * perUnit;
      shots.push({ file: `favicon-${ground}-${side}.png`, svg: `mark-${ground}.svg`, side, width: side, height: 14 * perUnit });
    }
  }
  for (const s of shots) {
    // Set inline rather than referenced: a page opened from a string may not load a file.
    const svg = fs.readFileSync(path.join(root, "mark", s.svg), "utf8")
      .replace(/<!--[\s\S]*?-->\s*/, "")
      .replace("<svg ", `<svg width="${s.width}" height="${s.height}" `);
    await page.setViewportSize({ width: s.side, height: s.side });
    await page.setContent(
      `<html><body style="margin:0;background:transparent;display:flex;align-items:center;justify-content:center;width:${s.side}px;height:${s.side}px">` +
      `${svg}</body></html>`);
    await page.screenshot({ path: path.join(out, s.file), omitBackground: true, clip: { x: 0, y: 0, width: s.side, height: s.side } });
    console.log(`wrote mark/png/${s.file}`);
  }
  await browser.close();
})();
