# design

Design tokens as JSON and CSS, the icon set as SVG sources, and the specimen sheet.

Extracted for the same reason as the schemas: four clients — the console, the two mobile
applications and the site — must agree on the palette, the type roles and the icons, and
none of them owns them. The mobile applications inherit the tokens, the type roles and
the voice, but not the density: a phone raises every hit target and drops the table to a
card list rather than shrinking the console.

Nothing is extracted yet. The design system is specified at
<https://agentiik.github.io/docs>.

## Licence

Two licences, because this repository holds two kinds of thing.

- **Code** — tokens, the CSS build, the icon sources as they are consumed by a client:
  Apache-2.0, see [LICENSE](LICENSE).
- **Assets and prose** — the specimen sheet, the written guidance, the mark's exported
  images: CC BY 4.0, see [LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt).

A software licence is a poor fit for a specimen sheet, and a content licence a poor fit
for a token file. [LICENSING.md](https://github.com/agentiik/.github/blob/main/LICENSING.md) has the reasoning.

The Agentiik name and mark are not covered by either: see [TRADEMARK.md](https://github.com/agentiik/.github/blob/main/TRADEMARK.md).

## Contributing

[CONTRIBUTING.md](https://github.com/agentiik/.github/blob/main/CONTRIBUTING.md), under the Developer Certificate of Origin 1.1.
