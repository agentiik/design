#!/usr/bin/env python3
"""Write tokens.css and the mark from tokens.json, or check that they are what it writes.

    python3 tools/build.py            write tokens.css and mark/*.svg
    python3 tools/build.py --check    refuse where any of them, or tokens.json, is wrong

tokens.json is the source, and tokens.css and the mark's files are generated from it and
committed, so that a client pins any of them at a tag and reads it as it is, with no build
of its own. They must never disagree, which is what --check holds, and tokens.json must
keep to what the documentation's Design system chapter fixes, which is what these rules
hold:

- Both grounds carry the same tokens, among them every one the chapter lists: a client
  switching ground finds each token it used on the other.
- Every colour is written #RRGGBB in capitals, so that one value is spelled one way and a
  search finds every use of it.
- running is the accent on each ground: the chapter makes it "the one state that borrows
  the accent hue", and two values that must be equal are one value typed twice.
- Each type role names a face the tokens declare, at a weight that face is loaded with: a
  weight nobody loads is drawn by the browser's synthesis, never by the typeface.
- Every gap is a whole number of base units, since the unit is what the rhythm is made of.
- The mark's bars sit on its grid, one row under the other without touching, the bars of a
  row side by side without touching, each row at a strength above none and at most full,
  and no corner rounder than half the thinnest bar: the chapter's "the grid and the three
  strengths are the whole specification" holds only while the specification is one a
  client can draw.

- Every icon is drawn as the chapter's Iconography says, stroke only on a 16px grid at
  1.5px with round caps and joins, no fill and no two-tone, in currentColor so that it takes
  muted or its state's colour from where it is set; and the set covers every run and step
  state, every port a workflow names by convention and every trigger_kind, under the
  names the documentation spells them with.

The specimen sheet, specimen.html, is generated too, from tools/specimen.html, with the
mark, the icons and a swatch, a pill, a type sample and a radius for every token set into
it, so that the sheet can never show a token the file lacks or miss one it has.

The lockup sets the outlines of mark/wordmark.svg beside the mark. tools/wordmark.py writes
those from the face, by hand, since it alone needs a font toolchain.

Standard library only: the design repository has nothing else to install, and a token
file that needs a toolchain to read is one a client stops reading.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tokens.json"
TARGET = ROOT / "tokens.css"
MARK = ROOT / "mark"
WORDMARK = MARK / "wordmark.svg"
ICONS = ROOT / "icons"
SPECIMEN_TEMPLATE = ROOT / "tools" / "specimen.html"
SPECIMEN = ROOT / "specimen.html"
SURFACES = ["sunken", "bg", "surface", "raised"]

# What the set must draw, as the documentation names it: the run states and a step's
# skipped (Run states), the ports a workflow names by convention (The graph and its ports,
# Merge strategies) and the trigger kinds a run records (Triggers). Controls are open: a
# view adds the one it draws.
REQUIRED = {
    "state": ["queued", "running", "waiting", "succeeded", "failed", "cancelled", "timed_out", "skipped"],
    "port": ["in", "out", "rejected", "error", "unmatched"],
    "trigger": ["manual", "schedule", "webhook", "event", "mcp", "terraform", "workflow"],
}
ICON_ROOT = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" fill="none" '
             'stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">')
ICON_NAME = re.compile(r"^(state|port|trigger|control)-([a-z]+(?:_[a-z]+)*)$")

# The tokens the Design system chapter lists, by the names it gives them. Anything else in
# tokens.json is derived from the chapter's mockups and named there too.
CORE = [
    "sunken", "bg", "surface", "raised", "faint", "muted", "text",
    "accentDim", "accent", "succeeded", "running", "waiting", "failed",
]

HEX = re.compile(r"^#[0-9A-F]{6}$")


def refuse(problems):
    for p in problems:
        print(f"tokens.json: {p}", file=sys.stderr)
    raise SystemExit(1)


def check_source(t):
    problems = []
    grounds = t["colour"]
    if set(grounds) != {"dark", "light"}:
        problems.append(f"colour has grounds {sorted(grounds)}, where dark and light are the two there are")
    names = {g: list(v) for g, v in grounds.items()}
    if len(set(map(tuple, map(sorted, names.values())))) != 1:
        only = {g: sorted(set(v) - set().union(*(set(o) for h, o in names.items() if h != g))) for g, v in names.items()}
        problems.append(f"the grounds carry different tokens: {only}")
    for g, values in grounds.items():
        for name in CORE:
            if name not in values:
                problems.append(f"{g} lacks {name}, which the Design system chapter lists")
        for name, value in values.items():
            if not HEX.match(value):
                problems.append(f"{g}.{name} is {value!r}, not #RRGGBB in capitals")
        if values.get("running") != values.get("accent"):
            problems.append(f"{g}.running is {values.get('running')}, where it is the accent, {values.get('accent')}")

    fonts = t["font"]
    for role, spec in t["type"].items():
        face = fonts.get(spec["font"])
        if face is None or not isinstance(face, dict):
            problems.append(f"type.{role} names the face {spec['font']!r}, which font does not declare")
            continue
        for key in ("weight", "weightActive", "weightName"):
            if key in spec and spec[key] not in face["weights"]:
                problems.append(f"type.{role}.{key} is {spec[key]}, a weight {spec['font']} is not loaded with")

    unit = t["density"]["unit"]
    for gap in t["density"]["gaps"]:
        if gap % unit:
            problems.append(f"the gap {gap} is not a whole number of {unit}px units")

    m = t["mark"]
    bottom = 0
    for i, row in enumerate(m["rows"]):
        if row["y"] < bottom or (i and row["y"] == bottom):
            problems.append(f"mark.rows[{i}] starts at {row['y']}, touching or overlapping the row above, which ends at {bottom}")
        bottom = row["y"] + row["height"]
        if not 0 < row["strength"] <= 1:
            problems.append(f"mark.rows[{i}].strength is {row['strength']}, where a strength is above 0 and at most 1")
        if m["radius"] * 2 > row["height"]:
            problems.append(f"mark.radius {m['radius']} is more than half mark.rows[{i}]'s height, {row['height']}")
        right = 0
        for j, bar in enumerate(row["bars"]):
            if bar["x"] < right or (j and bar["x"] == right):
                problems.append(f"mark.rows[{i}].bars[{j}] starts at {bar['x']}, touching or overlapping the bar before it")
            right = bar["x"] + bar["width"]
            if right > m["grid"]:
                problems.append(f"mark.rows[{i}].bars[{j}] ends at {right}, past the {m['grid']}-unit grid")

    if problems:
        refuse(problems)


def px(value):
    return f"{value:g}px"


def stack(face):
    names = [face["family"], *face["fallback"]]
    generic = {"sans-serif", "serif", "monospace", "ui-monospace", "system-ui"}
    return ", ".join(n if n in generic or " " not in n else f'"{n}"' for n in names)


def colours(values, indent):
    return "".join(f"{indent}--{name}: {value};\n" for name, value in values.items())


def render(t):
    out = []
    out.append("/* Generated by tools/build.py from tokens.json: edit that file and run the build, never this one.\n")
    out.append("   Light is the default ground; dark follows the reader's system unless data-theme=\"light\" is set\n")
    out.append("   on the root, and data-theme=\"dark\" forces it, as the site and the console both do. */\n\n")

    out.append(":root {\n")
    out.append("  color-scheme: light;\n")
    out.append(colours(t["colour"]["light"], "  "))
    out.append("\n")
    out.append(f"  --font-sans: {stack(t['font']['sans'])};\n")
    out.append(f"  --font-mono: {stack(t['font']['mono'])};\n")
    out.append("\n")
    for role, spec in t["type"].items():
        out.append(f"  --type-{role}-font: var(--font-{spec['font']});\n")
        size = spec["size"]
        if isinstance(size, dict):
            out.append(f"  --type-{role}-size-min: {px(size['min'])};\n")
            out.append(f"  --type-{role}-size-max: {px(size['max'])};\n")
        else:
            out.append(f"  --type-{role}-size: {px(size)};\n")
        for key in ("weight", "weightActive", "weightName"):
            if key in spec:
                out.append(f"  --type-{role}-{key}: {spec[key]};\n")
        if "tracking" in spec:
            out.append(f"  --type-{role}-tracking: {spec['tracking']};\n")
        if "case" in spec:
            out.append(f"  --type-{role}-case: {spec['case']};\n")
        if "lineHeight" in spec:
            lh = spec["lineHeight"]
            out.append(f"  --type-{role}-lineHeight-min: {px(lh['min'])};\n")
            out.append(f"  --type-{role}-lineHeight-max: {px(lh['max'])};\n")
    out.append("\n")
    d = t["density"]
    units = ", ".join(str(g // d["unit"]) for g in d["gaps"])
    out.append(f"  /* Gaps are {units} units: calc(var(--unit) * n). */\n")
    out.append(f"  --unit: {px(d['unit'])};\n")
    # The widths the console lays itself out by: under compact the sidebar folds to its icons, under
    # narrow it is a drawer. A media query reads no variable, so the console writes them in its own
    # queries too; these say what they are to anyone reading the tokens.
    out.append(f"  --window-compact: {px(d['window']['compact'])};\n")
    out.append(f"  --window-narrow: {px(d['window']['narrow'])};\n")
    for group in ("bar", "sidebar", "row", "padding", "radius", "border"):
        for name, value in d[group].items():
            out.append(f"  --{group}-{name}: {px(value)};\n")
    out.append("}\n\n")

    dark = colours(t["colour"]["dark"], "    ")
    out.append("@media (prefers-color-scheme: dark) {\n")
    out.append("  :root:not([data-theme=\"light\"]) {\n")
    out.append("    color-scheme: dark;\n")
    out.append(dark)
    out.append("  }\n")
    out.append("}\n\n")
    out.append(":root[data-theme=\"dark\"] {\n")
    out.append("  color-scheme: dark;\n")
    out.append(colours(t["colour"]["dark"], "  "))
    out.append("}\n")
    return "".join(out)


def mark_height(m):
    return max(row["y"] + row["height"] for row in m["rows"])


def mark_rects(m):
    out = []
    for row in m["rows"]:
        rects = "".join(
            f'<rect x="{bar["x"]:g}" y="{row["y"]:g}" width="{bar["width"]:g}" height="{row["height"]:g}" rx="{m["radius"]:g}"/>'
            for bar in row["bars"]
        )
        out.append(rects if row["strength"] == 1 else f'<g opacity="{row["strength"]:g}">{rects}</g>')
    return "".join(out)


def svg(view_box, body, what):
    return (
        f"<!-- Generated by tools/build.py from tokens.json: {what}. -->\n"
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" role="img" aria-label="Agentiik">{body}</svg>\n'
    )


def wordmark():
    """The outline and ink box tools/wordmark.py wrote."""
    text = WORDMARK.read_text(encoding="utf-8")
    box = [float(v) for v in re.search(r'viewBox="([^"]+)"', text).group(1).split()]
    path = re.search(r'<path d="([^"]+)"/>', text).group(1)
    return path, box


def render_mark(t):
    """Every file of mark/ but the wordmark, by name."""
    m = t["mark"]
    grid, height, clear = m["grid"], mark_height(m), m["clearSpace"]
    rects = mark_rects(m)
    side = grid + 2 * clear
    square = f"{-clear:g} {-(side - height) / 2:g} {side:g} {side:g}"
    path, box = wordmark()
    offset = grid + m["lockup"]["gap"]
    width = round(offset + box[0] + box[2], 3)
    files = {
        "mark.svg": svg(f"0 0 {grid:g} {height:g}", f'<g fill="currentColor">{rects}</g>',
                        "the mark in the colour of the text around it, for a client that sets it to the accent"),
    }
    for ground in ("light", "dark"):
        c = t["colour"][ground]
        files[f"mark-{ground}.svg"] = svg(
            f"0 0 {grid:g} {height:g}", f'<g fill="{c["accent"]}">{rects}</g>',
            f"the mark in the {ground} ground's accent")
        files[f"mark-square-{ground}.svg"] = svg(
            square, f'<g fill="{c["accent"]}">{rects}</g>',
            f"the mark in the {ground} ground's accent, centred on a square with its clear space")
        files[f"lockup-{ground}.svg"] = svg(
            f"0 0 {width:g} {height:g}",
            f'<g fill="{c["accent"]}">{rects}</g><path fill="{c["text"]}" transform="translate({offset:g} 0)" d="{path}"/>',
            f"the lockup on the {ground} ground, the mark in its accent and the wordmark in its text colour")
    return files


def check_icons():
    """The icons by group, once every one keeps to the Iconography rules."""
    problems = []
    groups = {}
    for path in sorted(ICONS.glob("*.svg")):
        m = ICON_NAME.match(path.stem)
        if not m:
            problems.append(f"icons/{path.name} is not named group-name, the group one of state, port, trigger, control")
            continue
        groups.setdefault(m.group(1), []).append(m.group(2))
        text = path.read_text(encoding="utf-8")
        body = text.strip()
        if not body.startswith(ICON_ROOT) or not body.endswith("</svg>"):
            problems.append(f"icons/{path.name} does not open with the one root every icon has: 16px, stroke only at 1.5 in currentColor, round caps and joins")
            continue
        inner = body[len(ICON_ROOT):-len("</svg>")]
        for pattern, why in ((r"\sfill=", "a fill of its own"), (r"\sstroke=", "a stroke colour of its own"),
                             (r"stroke-width", "a stroke width of its own"), (r"\s(style|class)=", "a style or class"),
                             (r"<(text|image|style|use|linearGradient|radialGradient)\b", "text, an image, a style, a reference or a gradient")):
            if re.search(pattern, inner):
                problems.append(f"icons/{path.name} carries {why}, where every icon is one stroke in currentColor")
    for group, names in REQUIRED.items():
        missing = [n for n in names if n not in groups.get(group, [])]
        if missing:
            problems.append(f"icons/ has no {group} icon for {', '.join(missing)}")
    if problems:
        for p in problems:
            print(p, file=sys.stderr)
        raise SystemExit(1)
    # The documented order first, since a client lays states out in it, then the rest by name.
    def ordered(group):
        known = REQUIRED.get(group, [])
        return [n for n in known if n in groups[group]] + sorted(n for n in groups[group] if n not in known)
    return {g: ordered(g) for g in ("state", "port", "trigger", "control") if g in groups}


# What each type role is shown setting on the specimen: text it would carry in the console.
SAMPLES = {
    "wordmark": "agentiik",
    "pageTitle": "monthly-invoicing",
    "sectionTitle": "Reading a run, end to end",
    "navigation": "Runs · Workflows · Statistics · Bricks · Sharing",
    "control": "Replay from invoice",
    "body": "Failures sit in a band above the table: they are almost always why the page is opened.",
    "columnHead": "Started",
    "name": "finance/monthly-invoicing · alice · invoice.ok",
    "identifier": "01JMZ8V1P9C4 · a3f9c1e · exit 108",
    "code": "invoice:\n  needs:\n    - { step: normalize, port: ok, as: in }",
}
GROUP_TITLES = {"state": "States", "port": "Ports", "trigger": "Trigger kinds", "control": "Controls"}


def html_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def type_style(role, spec):
    size = f"var(--type-{role}-size-max)" if isinstance(spec["size"], dict) else f"var(--type-{role}-size)"
    parts = [f"font-family: var(--type-{role}-font)", f"font-size: {size}", f"font-weight: var(--type-{role}-weight)"]
    if "tracking" in spec:
        parts.append(f"letter-spacing: var(--type-{role}-tracking)")
    if "case" in spec:
        parts.append(f"text-transform: var(--type-{role}-case)")
    if "lineHeight" in spec:
        parts.append(f"line-height: var(--type-{role}-lineHeight-max); white-space: pre")
    return "; ".join(parts)


def type_caption(t, role, spec):
    face = t["font"][spec["font"]]["family"]
    size = spec["size"]
    size = f"{size['min']:g} to {size['max']:g}px" if isinstance(size, dict) else f"{size:g}px"
    extra = []
    for key, word in (("weightActive", "when active"), ("weightName", "on a name")):
        if key in spec:
            extra.append(f"{spec[key]} {word}")
    if "lineHeight" in spec:
        extra.append(f"line height {spec['lineHeight']['min']:g} to {spec['lineHeight']['max']:g}px")
    return f"{face} {size} / {spec['weight']}" + (", " + ", ".join(extra) if extra else "")


def render_specimen(t, icons):
    m = t["mark"]
    rects = mark_rects(m)
    path, box = wordmark()
    offset = m["grid"] + m["lockup"]["gap"]
    width = round(offset + box[0] + box[2], 3)
    names = [n for n in t["colour"]["light"] if n not in SURFACES]
    swatches = "\n".join(
        f'    <div class="swatch"><div class="chip" style="background: var(--{n})"></div>'
        f'<div class="label"><code>{n}</code><code data-hex="--{n}"></code></div></div>' for n in names)
    pills = "\n".join(f'    <span class="pill {s}">{s}</span>' for s in REQUIRED["state"])
    types = "\n".join(
        f'    <span class="role"><code>{role}</code><br>{type_caption(t, role, spec)}</span>'
        f'<span style="{type_style(role, spec)}">{html_escape(SAMPLES[role])}</span>'
        for role, spec in t["type"].items())
    radii = "\n".join(
        f'    <div class="spec"><div class="radius" style="border-radius: var(--radius-{n})"></div><code>radius.{n}</code></div>'
        for n in t["density"]["radius"])
    blocks = []
    for group, members in icons.items():
        cells = "".join(
            f'<div class="icon {group}-{n}">{(ICONS / f"{group}-{n}.svg").read_text(encoding="utf-8").strip()}<code>{n}</code></div>'
            for n in members)
        blocks.append(f'  <h3 style="margin-top: 6px">{GROUP_TITLES[group]}</h3>\n  <div class="icons" style="margin-bottom: 18px">{cells}</div>')
    values = {
        "font-source": html_escape(t["font"]["source"]),
        "mark": f'<g fill="currentColor">{rects}</g>',
        "mark-rects": rects,
        "wordmark": path,
        "lockup-width": f"{width:g}",
        "lockup-width-3": f"{width * 3:g}",
        "lockup-offset": f"{offset:g}",
        "swatches": swatches,
        "pills": pills,
        "type": types,
        "radii": radii,
        "icons": "\n".join(blocks),
    }
    page = SPECIMEN_TEMPLATE.read_text(encoding="utf-8")
    page = re.sub(r"\{\{([a-z0-9-]+)\}\}", lambda x: values[x.group(1)], page)
    # After the doctype, never before it: a comment ahead of it puts a browser in quirks mode.
    doctype, rest = page.split("\n", 1)
    return f"{doctype}\n<!-- Generated by tools/build.py from tools/specimen.html and tokens.json: edit those, never this file. -->\n{rest}"


def outputs(t):
    files = {TARGET: render(t)}
    for name, text in render_mark(t).items():
        files[MARK / name] = text
    icons = check_icons()
    files[ICONS / "icons.json"] = json.dumps(icons, indent=2) + "\n"
    files[SPECIMEN] = render_specimen(t, icons)
    return files


def main():
    checking = "--check" in sys.argv[1:]
    tokens = json.loads(SOURCE.read_text(encoding="utf-8"))
    check_source(tokens)
    files = outputs(tokens)
    if checking:
        stale = [p.relative_to(ROOT).as_posix() for p, text in files.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print(f"{', '.join(stale)}: not what tokens.json writes: run python3 tools/build.py and commit them", file=sys.stderr)
            raise SystemExit(1)
        print("tokens.json keeps to the rules, and every file generated from it is what it writes")
        return
    for path, text in files.items():
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
