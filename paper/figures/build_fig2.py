#!/usr/bin/env python3
"""Figure 2: forbidden attempts per Bedrock model, over delivered samples.

Standard library only. The bars are read from the Attempted cells of Tables 16
and 18 in ../REPORT.md, so every bar is a table cell, and the script prints the
cells it used. Panel A is Table 16 (the artifact_note and result_field arms);
panel B is Table 18 (the separate tool_error and multi_step rerun with the
error text delivered). The panels are separate runs and nothing here adds them.

The SVG uses only rect, line and text elements, in the style of pipeline.svg,
so the paper's SVG-to-TikZ step converts it. Run:

    python3 -I build_fig2.py

It writes bedrock-attempts.svg beside this script.
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "..", "REPORT.md")
OUT = os.path.join(HERE, "bedrock-attempts.svg")

# The ten Bedrock models, in the row order of Table 16.
MODELS = [
    "qwen3-next-80b-a3b",
    "deepseek.v3.2",
    "mistral-large-3-675b",
    "gpt-oss-120b",
    "nova-pro",
    "qwen3-32b",
    "qwen3-coder-30b-a3b",
    "ministral-3-14b",
    "llama-3.3-70b",
    "llama-3.1-8b",
]
SUITES = ["base", "stronger"]
PANELS = [
    ("A. Note and result-field arms", "artifact_note and result_field, Table 16", 16),
    ("B. Error arms, text delivered", "tool_error and multi_step rerun, Table 18", 18),
]

INK = "#1f2a44"
MUTED = "#5a6478"
GRID = "#c9ced8"
FILL = {"base": "#9fb3d1", "stronger": "#1f2a44"}

WIDTH, LABEL_X = 640, 122
PANEL_X = {16: 130.0, 18: 390.0}
SCALE = 200.0 / 0.7  # pixels per unit rate; the axis runs from 0 to 0.7
TICKS = [0.0, 0.2, 0.4, 0.6]
TOP, ROW, BAR = 48.0, 24.0, 8.0


def attempted_cells(lines, number):
    """Map (model, suite) to the Attempted cell of the numbered table."""
    start = next(i for i, x in enumerate(lines) if x.startswith(f"*Table {number}. "))
    rows = []
    for x in lines[start + 2:]:
        if not x.startswith("|"):
            break
        rows.append([c.strip() for c in x.strip().strip("|").split("|")])
    header, body = rows[0], rows[2:]
    col = header.index("Attempted")
    cells = {}
    for r in body:
        m = re.match(r"(\d+)/(\d+)\b", r[col])
        if m:
            cells[(r[0], r[1])] = (r[col], int(m.group(1)), int(m.group(2)))
    return cells


def text(x, y, s, size, fill=INK, anchor="start", bold=False):
    weight = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{weight} fill="{fill}"'
            f' text-anchor="{anchor}">{s}</text>')


def rect(x, y, w, h, fill):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/>'


def line(x1, y1, x2, y2, stroke, width, dash=None):
    pattern = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
            f' stroke="{stroke}" stroke-width="{width}"{pattern}/>')


def main():
    lines = open(REPORT, encoding="utf-8").read().split("\n")
    data = {}
    for _, _, number in PANELS:
        cells = attempted_cells(lines, number)
        for model in MODELS:
            for suite in SUITES:
                data[(number, model, suite)] = cells[(model, suite)]

    bottom = TOP + ROW * len(MODELS)
    height = int(bottom + 52)
    grid, bars, labels = [], [], []
    for title, subtitle, number in PANELS:
        x0 = PANEL_X[number]
        labels.append(text(x0, 16, title, 10, bold=True))
        labels.append(text(x0, 29, subtitle, 9, fill=MUTED))
        for t in TICKS:
            x = x0 + t * SCALE
            if t:
                grid.append(line(x, TOP - 6, x, bottom, GRID, "0.6", "2 2"))
            labels.append(text(x, bottom + 12, f"{t:.1f}", 8, fill=MUTED, anchor="middle"))
        grid.append(line(x0, TOP - 6, x0, bottom, MUTED, "0.8"))
        labels.append(text(x0 + 0.3 * SCALE, bottom + 25, "attempts / delivered samples", 9,
                           fill=MUTED, anchor="middle"))
        for i, model in enumerate(MODELS):
            for j, suite in enumerate(SUITES):
                cell, k, n = data[(number, model, suite)]
                y = TOP + ROW * i + 3 + j * (BAR + 1)
                w = k / n * SCALE
                if k:
                    bars.append(rect(x0, y, w, BAR, FILL[suite]))
                labels.append(text(x0 + w + 3, y + 7, f"{k}/{n}", 8))
    for i, model in enumerate(MODELS):
        labels.append(text(LABEL_X, TOP + ROW * i + 13, model, 10, anchor="end"))
    legend_y = bottom + 42
    for j, suite in enumerate(SUITES):
        x = 10 + j * 90
        bars.append(rect(x, legend_y - 7, 10, BAR, FILL[suite]))
        labels.append(text(x + 14, legend_y, f"{suite} suite", 9))

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}">']
    svg += grid + bars + labels + ["</svg>"]
    with open(OUT, "w", encoding="ascii") as f:
        f.write("\n".join(svg) + "\n")

    for _, _, number in PANELS:
        total = 0
        for model in MODELS:
            for suite in SUITES:
                cell, k, n = data[(number, model, suite)]
                total += k
                print(f"Table {number}\t{model}\t{suite}\t{k}/{n}\t{cell}")
        print(f"Table {number}\tattempts in the panel (not drawn): {total}")


if __name__ == "__main__":
    main()
