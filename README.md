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

To change a value, change it on the site first, then in `tokens.json`, run `python3 tools/build.py`, and commit what it writes.

## The mark

`tokens.json` holds the mark as the chapter specifies it, its grid, its rows and their three strengths, its clear space and its lockup, and `tools/build.py` draws every file of [mark/](mark) from it:

| File | What it is |
| --- | --- |
| `mark.svg` | The mark in `currentColor`, for a client that sets it to the accent. |
| `mark-light.svg`, `mark-dark.svg` | The mark in each ground's accent, 16 by 14 units. |
| `mark-square-light.svg`, `mark-square-dark.svg` | The mark centred on a 24-unit square that holds its clear space, for an avatar or an application icon. |
| `lockup-light.svg`, `lockup-dark.svg` | The mark and the wordmark, nine units apart on one optical centre, the wordmark in the ground's `text`. |
| `wordmark.svg` | The wordmark as outlines of Archivo Bold, written by `tools/wordmark.py` from the face, by hand, since a lockup that asks for a font draws in whatever the viewer has. |
| `png/` | The square at 2 to 32 pixels a unit and the mark alone at 1 and 2, as favicons, transparent, for each ground: `npm install && npm run export`. |

## Icons

[icons/](icons) holds one SVG per icon, named `group-name`: every run and step state, every port a workflow names by convention, every `trigger_kind`, and the controls a view draws, stroke only on a 16px grid at 1.5px in `currentColor`. `tools/build.py` refuses an icon that breaks those rules or a state, port or trigger kind with none, and writes [icons/icons.json](icons/icons.json), the names by group, states in the documented order.

## The specimen sheet

[specimen.html](specimen.html) draws every token, type role, measure, state pill, the mark and every icon, each beside the chapter's rule it shows and a link to it, on the reader's ground or on the one its address names (`specimen.html#dark`). `tools/build.py` writes it from `tools/specimen.html`, so it can never show a token the file lacks or miss one it has.

The `specimen` workflow renders it on both grounds and compares each render, pixel for pixel, with the references in [tests/specimen](tests/specimen), so a token edit fails there first, as the change it makes. A change that was meant commits new references with it, rendered by the workflow itself: dispatched on the branch with `references` set, it renders them in the Playwright image `package.json` pins and commits them there, since a reference taken anywhere else would not match what the check renders. A failed run also keeps its renders and their differences as its `specimen-renders` artifact, to see what changed.

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
