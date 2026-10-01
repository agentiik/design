// The visual check of the specimen sheet: the page rendered on each ground and compared with
// the images committed beside it, so that a token edit shows up here as the change it makes,
// and a change nobody asked for fails.
//
// The references are rendered in the image the workflow runs in, mcr.microsoft.com/playwright
// at the version package.json pins, since text is antialiased by whatever the machine has and
// two machines disagree about pixels nobody would. A reference taken anywhere else is one the
// check would refuse on its first run.
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "tests",
  snapshotPathTemplate: "tests/specimen/{arg}{ext}",
  reporter: [["list"]],
  use: {
    browserName: "chromium",
    viewport: { width: 1320, height: 900 },
    deviceScaleFactor: 1,
  },
  expect: {
    // Pixel for pixel: a token is often one colour a few percent away from another, and any
    // tolerance wide enough to forgive antialiasing would forgive that too.
    toHaveScreenshot: { maxDiffPixels: 0, animations: "disabled" },
  },
});
