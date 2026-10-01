const fs = require("fs");
const path = require("path");
const { test, expect } = require("@playwright/test");

const root = path.resolve(__dirname, "..");
const specimen = "file://" + path.join(root, "specimen.html");
const tokens = JSON.parse(fs.readFileSync(path.join(root, "tokens.json"), "utf8"));

// Every face at every weight tokens.json loads it with, as a CSS font shorthand.
const faces = Object.values(tokens.font)
  .filter((f) => typeof f === "object")
  .flatMap((f) => f.weights.map((w) => `${w} 16px "${f.family}"`));

for (const ground of ["light", "dark"]) {
  test(`the specimen on the ${ground} ground is what it was`, async ({ page }) => {
    await page.goto(`${specimen}#${ground}`, { waitUntil: "networkidle" });
    // The faces come from Google Fonts, and a page captured before one arrives is drawn in
    // the fallback stack: a different height, and a reference nobody should keep. Each face
    // is asked for, and the test stops where one did not come.
    const missing = await page.evaluate(async (faces) => {
      await Promise.all(faces.map((f) => document.fonts.load(f)));
      await document.fonts.ready;
      return faces.filter((f) => !document.fonts.check(f));
    }, faces);
    expect(missing, "faces that did not load").toEqual([]);
    await expect(page).toHaveScreenshot(`specimen-${ground}.png`, { fullPage: true });
  });
}
