# design

Design tokens as JSON and CSS, the icon set as SVG sources, and the specimen sheet.

Extracted for the same reason as the schemas: four clients (the console, the two mobile
applications and the site) must agree on the palette, the type roles and the icons, and
none of them owns them. The mobile applications inherit the tokens, the type roles and
the voice, but not the density: a phone raises every hit target and drops the table to a
card list rather than shrinking the console.

The design system is specified at <https://agentiik.github.io/docs#design>, which decides every value here: this repository publishes them, it does not choose them.

## Tokens

| File | What it is |
| --- | --- |
| [tokens.json](tokens.json) | The source: the colours of both grounds, the two faces and where they are served from, the type roles, and the density scale. |
| [tokens.css](tokens.css) | The same values as CSS custom properties, generated from `tokens.json` and committed, light by default, dark from the reader's system unless `data-theme="light"` is set on the root, and forced by `data-theme="dark"`. |
| [tools/build.py](tools/build.py) | Writes `tokens.css`, and with `--check` refuses where it differs from what `tokens.json` writes or where `tokens.json` breaks a rule the script states at its top. CI runs the same command. |

A client pins a tag, since token names and meanings are what a release promises and a branch promises nothing: `https://raw.githubusercontent.com/agentiik/design/vX.Y.Z/tokens.css`, or `tokens.json` for a client that generates its own form, as `agk console` does.

The colour names are the chapter's own, so what a client writes is what the documentation says: `sunken`, `bg`, `surface`, `raised`, `faint`, `muted`, `text`, `accentDim`, `accent`, and the state ramp `succeeded`, `running`, `waiting`, `failed`. The others are what the chapter's mockups are drawn with: `line`, the hairline of rows and dividers, and `lineStrong`, the outline of a control, a chip and a pane, the two hairlines elevation is made of; `accentLine`, the outline of what is filled with `accentDim`, the `running` pill, the active view and the selected chip among them; `onAccent`, the ink on a solid accent fill; and the fill and outline of each other state's pill, `succeededFill` and `succeededLine`, `waitingFill` and `waitingLine`, `failedFill` and `failedLine`. A faint state's pill, `queued`, `skipped` or `cancelled`, is `sunken` outlined in `lineStrong`.

To change a value, change it on the site first, then in `tokens.json`, run `python3 tools/build.py`, and commit both files.

## Licence

Two licences, because this repository holds two kinds of thing.

- **Code**: tokens, the CSS build, the icon sources as they are consumed by a client:
  Apache-2.0, see [LICENSE](LICENSE).
- **Assets and prose**: the specimen sheet, the written guidance, the mark's exported
  images: CC BY 4.0, see [LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt).

A software licence is a poor fit for a specimen sheet, and a content licence a poor fit
for a token file. [LICENSING.md](https://github.com/agentiik/.github/blob/main/LICENSING.md) has the reasoning.

The Agentiik name and mark are not covered by either: see [TRADEMARK.md](https://github.com/agentiik/.github/blob/main/TRADEMARK.md).

## Contributing

[CONTRIBUTING.md](https://github.com/agentiik/.github/blob/main/CONTRIBUTING.md), under the Developer Certificate of Origin 1.1.
