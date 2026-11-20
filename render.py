#!/usr/bin/env python3
"""Draw "The World in One Page" — a newspaper front page summing up
Friday 20 November 2026 world news. Pillow, stdlib otherwise.
Deterministic: same brief -> same PNG bytes.

Usage: python3 render.py [out.png]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 251, 244)
INK = (26, 26, 26)
RED = (178, 34, 34)
GREY = (110, 108, 100)
RULE = (180, 175, 165)
BLUE = (31, 68, 130)
GOLD = (201, 162, 39)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by measured width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, x, y, text, fnt, max_w, leading, max_lines, fill=INK):
    """Draw wrapped paragraph, capped at max_lines with an ellipsis.
    Returns (lines_drawn, height_used)."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
        lines[-1] = (lines[-1] + " ...").strip()
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return len(lines), len(lines) * leading


def fit(draw, text, fnt_path, size, max_w):
    """Shrink font until text fits max_w; returns font."""
    while size > 12:
        f = font(fnt_path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(fnt_path, 12)


# ---------------------------------------------------------------- icons
# Each icon draws inside the square (x, y, s) and takes only (draw, x, y, s).

def icon_flags(draw, x, y, s):
    """Two small flags side by side: Union Jack-ish cross + EU stars."""
    w = s // 2 - 4
    h = int(s * 0.62)
    y0 = y + (s - h) // 2
    # left flag: blue field, white + red cross
    draw.rectangle([x, y0, x + w, y0 + h], fill=BLUE, outline=INK, width=2)
    draw.rectangle([x + w // 2 - 3, y0, x + w // 2 + 3, y0 + h], fill=(240, 240, 240))
    draw.rectangle([x, y0 + h // 2 - 3, x + w, y0 + h // 2 + 3], fill=(240, 240, 240))
    draw.rectangle([x + w // 2 - 1, y0, x + w // 2 + 1, y0 + h], fill=RED)
    draw.rectangle([x, y0 + h // 2 - 1, x + w, y0 + h // 2 + 1], fill=RED)
    # right flag: EU blue with a ring of gold stars
    x2 = x + w + 8
    draw.rectangle([x2, y0, x2 + w, y0 + h], fill=(0, 51, 153), outline=INK, width=2)
    import math
    cx, cy, r = x2 + w // 2, y0 + h // 2, min(w, h) // 2 - 8
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)


def icon_bridge(draw, x, y, s):
    """A suspension bridge over water."""
    deck = y + int(s * 0.55)
    draw.rectangle([x, deck, x + s, deck + 6], fill=INK)
    tw = s // 5
    for tx in (x + tw, x + s - tw * 2):
        draw.rectangle([tx, y + s // 8, tx + 6, deck], fill=INK)
    draw.line([x, deck, x + tw + 3, y + s // 8], fill=INK, width=2)
    draw.line([x + s, deck, x + s - tw - 3, y + s // 8], fill=INK, width=2)
    for i in range(5):
        cx = x + s // 6 + i * s // 6
        draw.line([cx, deck, cx, deck - 14], fill=INK, width=1)
    wy = deck + 16
    for i in range(4):
        draw.arc([x + i * s // 4, wy, x + (i + 1) * s // 4 + 4, wy + 16],
                 0, 180, fill=BLUE, width=3)


def icon_chart(draw, x, y, s):
    """Bars with a falling arrow."""
    bw = s // 6
    heights = [0.35, 0.55, 0.45, 0.75, 0.5]
    base = y + int(s * 0.82)
    for i, hf in enumerate(heights):
        bx = x + i * (bw + 6)
        bh = int(s * hf)
        draw.rectangle([bx, base - bh, bx + bw, base], fill=BLUE if i < 4 else RED)
    draw.line([x, y + s // 6, x + s, y + s // 3], fill=RED, width=4)
    ax, ay = x + s - 6, y + s // 3
    draw.polygon([(ax, ay), (ax - 14, ay - 2), (ax - 2, ay + 12)], fill=RED)


def icon_shield(draw, x, y, s):
    """A shield with a keyhole."""
    pts = [(x + s // 2, y + 2), (x + s - 2, y + s // 5),
           (x + s - 2, y + int(s * 0.55)), (x + s // 2, y + s - 2),
           (x + 2, y + int(s * 0.55)), (x + 2, y + s // 5)]
    draw.polygon(pts, fill=BLUE, outline=INK)
    cx, cy = x + s // 2, y + int(s * 0.42)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=GOLD)
    draw.polygon([(cx - 4, cy + 4), (cx + 4, cy + 4), (cx + 7, cy + 16),
                  (cx - 7, cy + 16)], fill=GOLD)


def icon_scales(draw, x, y, s):
    """Scales of justice."""
    cx = x + s // 2
    draw.line([cx, y + 6, cx, y + s - 14], fill=INK, width=4)
    draw.line([x + 6, y + 14, x + s - 6, y + 14], fill=INK, width=4)
    for sx in (x + 6, x + s - 6):
        draw.line([sx, y + 14, sx - 14, y + int(s * 0.55)], fill=INK, width=2)
        draw.line([sx, y + 14, sx + 14, y + int(s * 0.55)], fill=INK, width=2)
        draw.arc([sx - 16, y + int(s * 0.5), sx + 16, y + int(s * 0.72)],
                 0, 180, fill=INK, width=3)
    draw.rectangle([x + s // 2 - 22, y + s - 14, x + s // 2 + 22, y + s - 8],
                   fill=INK)


def icon_globe(draw, x, y, s):
    """A globe with meridians."""
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=4,
                 fill=(198, 222, 240))
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=INK,
                 width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=INK, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 360, fill=INK,
             width=2)
    draw.polygon([(cx - 14, cy - 8), (cx + 2, cy - 18), (cx + 16, cy - 4),
                  (cx + 6, cy + 8), (cx - 12, cy + 6)], fill=(76, 140, 74))


def icon_rocket(draw, x, y, s):
    """A small rocket, nose up."""
    cx = x + s // 2
    draw.polygon([(cx, y + 2), (cx + 16, y + int(s * 0.4)),
                  (cx + 12, y + int(s * 0.75)), (cx - 12, y + int(s * 0.75)),
                  (cx - 16, y + int(s * 0.4))], fill=INK)
    draw.ellipse([cx - 8, cy - 6, cx + 8, cy + 10], fill=GOLD)
    draw.polygon([(cx - 12, y + int(s * 0.7)), (cx - 26, y + s - 6),
                  (cx - 6, y + int(s * 0.82))], fill=RED)
    draw.polygon([(cx + 12, y + int(s * 0.7)), (cx + 26, y + s - 6),
                  (cx + 6, y + int(s * 0.82))], fill=RED)
    draw.polygon([(cx - 6, y + int(s * 0.78)), (cx + 6, y + int(s * 0.78)),
                  (cx, y + s - 2)], fill=(230, 120, 40))


ICONS = {"flags": icon_flags, "bridge": icon_bridge, "chart": icon_chart,
         "shield": icon_shield, "scales": icon_scales, "globe": icon_globe,
         "rocket": icon_rocket}

# ---------------------------------------------------------------- content

MASTHEAD = "THE WORLD IN ONE PAGE"
DATELINE = "FRIDAY, 20 NOVEMBER 2026"
DECK = "Friday's world news \u2014 the reset, the retaliation, the record IPO \u2014 on one page."

LEAD = {
    "kicker": "BRUSSELS  \u00b7  BREXIT RESET",
    "icon": "flags",
    "headline": "UK and EU seal reset deal at Brussels summit",
    "body": ("Britain and the EU agree deals on food trade, youth mobility and "
             "carbon trading \u2014 the biggest reset since Brexit. Young people "
             "under 31 will get 100,000 visas a year each way; student fees are "
             "left for six more months of talks."),
}

GRID = [
    {"kicker": "KYIV  \u00b7  WAR", "icon": "bridge",
     "headline": "Russia hits three Kyiv bridges in overnight barrage",
     "body": ("Eight killed as missiles and drones strike the Dnipro crossings, "
              "hours after Putin vowed a \u2018painful\u2019 reply to the Crimea "
              "bridge attacks.")},
    {"kicker": "MARKETS  \u00b7  AI", "icon": "chart",
     "headline": "Anthropic shares slide after record $107.3bn debut",
     "body": ("Shares fall 5% after hours after the biggest IPO ever; the debut "
              "had surged 39% before fading, and Asian AI stocks sold off.")},
    {"kicker": "WASHINGTON  \u00b7  CYBER", "icon": "shield",
     "headline": "White House replaces cyber chief after tech outages",
     "body": ("The cyber-security director is out after a string of outages, as "
              "the administration bows to pressure over the failures.")},
    {"kicker": "TEXAS  \u00b7  JUSTICE", "icon": "scales",
     "headline": "Texas execution takes over an hour",
     "body": ("Staff struggled to find a vein as Reinaldo Dennes was put to "
              "death; he moaned about pain during the prolonged procedure.")},
    {"kicker": "SHENZHEN  \u00b7  SUMMIT", "icon": "flags",
     "headline": "Trump, Xi and Putin meet \u2014 with little to show",
     "body": ("The first trilateral of the three leaders ends with camaraderie "
              "on show and few results, as Putin vows retaliation over Crimea.")},
    {"kicker": "THE HAGUE  \u00b7  JUSTICE", "icon": "globe",
     "headline": "After the genocide verdict, what next for the Rohingya?",
     "body": ("A day after the world court ruled Myanmar committed genocide, "
              "attention turns to return, compensation \u2014 and whether the "
              "world will act.")},
]

BRIEFS = [
    ("NEW YORK", "Mamdani unveils a plan to close the Rikers Island jail complex."),
    ("SPACE", "BepiColombo reaches Mercury after eight years; orbit burn on Saturday."),
    ("SOUTH ASIA", "Pakistan minister visits India for the first time since the 2025 war."),
]

FOOTER = ("Sources: Al Jazeera \u00b7 BBC \u00b7 The Guardian \u00b7 Deutsche Welle \u00b7 "
          "NYT \u00b7 CNN \u00b7 NPR \u00b7 Bloomberg \u00b7 Reuters  \u2014  all reporting "
          "published on 20 November 2026.")

# ---------------------------------------------------------------- layout

def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36                      # side margin
    CW = W - 2 * M              # content width

    # Masthead
    mast = fit(d, MASTHEAD, SERIF_B, 58, CW)
    mw = d.textlength(MASTHEAD, font=mast)
    d.text(((W - mw) / 2, 26), MASTHEAD, font=mast, fill=INK)
    d.line([M, 96, W - M, 96], fill=INK, width=3)
    d.line([M, 101, W - M, 101], fill=INK, width=1)

    # Dateline + deck
    date_f = font(SANS_B, 17)
    dw = d.textlength(DATELINE, font=date_f)
    d.text(((W - dw) / 2, 112), DATELINE, font=date_f, fill=RED)
    deck_f = font(SERIF, 20)
    dekw = d.textlength(DECK, font=deck_f)
    d.text(((W - dekw) / 2, 140), DECK, font=deck_f, fill=INK)
    d.line([M, 172, W - M, 172], fill=RULE, width=1)

    # ---- Lead story: headline across, icon left, body right
    y = 186
    kick_f = font(SANS_B, 15)
    d.text((M, y), LEAD["kicker"], font=kick_f, fill=RED)
    y += 24
    head_f = font(SERIF_B, 34)
    _, hh = draw_para(d, M, y, LEAD["headline"], head_f, CW, 40, 2)
    y += hh + 10
    icon_s = 150
    ICONS[LEAD["icon"]](d, M + 8, y + 4, icon_s)
    body_f = font(SANS, 20)
    bx = M + icon_s + 36
    bw = W - M - bx
    draw_para(d, bx, y + 2, LEAD["body"], body_f, bw, 27, 5)
    y += icon_s + 14
    d.line([M, y, W - M, y], fill=INK, width=2)
    y += 14

    # ---- Grid: 2 columns x 3 rows
    gutter = 24
    col_w = (CW - gutter) // 2
    row_h = 130
    for i, story in enumerate(GRID):
        col = i % 2
        row = i // 2
        sx = M + col * (col_w + gutter)
        sy = y + row * row_h
        isz = 84
        ICONS[story["icon"]](d, sx, sy + 6, isz)
        tx = sx + isz + 14
        tw = sx + col_w - tx
        d.text((tx, sy), story["kicker"], font=font(SANS_B, 12), fill=RED)
        hf = font(SERIF_B, 20)
        _, used = draw_para(d, tx, sy + 18, story["headline"], hf, tw, 24, 2)
        bf = font(SANS, 15)
        draw_para(d, tx, sy + 18 + used + 4, story["body"], bf, tw, 19, 3)
        if col == 0:
            d.line([sx + col_w + gutter // 2, sy + 4,
                    sx + col_w + gutter // 2, sy + row_h - 14],
                   fill=RULE, width=1)
        if row < 2:
            d.line([sx, sy + row_h - 8, sx + col_w, sy + row_h - 8],
                   fill=RULE, width=1)
    y += 3 * row_h + 6
    d.line([M, y, W - M, y], fill=INK, width=2)
    y += 12

    # ---- Also strip: three briefs
    also_f = font(SANS_B, 14)
    d.text((M, y), "ALSO", font=also_f, fill=RED)
    y += 22
    bw3 = (CW - 2 * gutter) // 3
    for i, (kick, text) in enumerate(BRIEFS):
        bx = M + i * (bw3 + gutter)
        d.text((bx, y), kick, font=font(SANS_B, 12), fill=GREY)
        draw_para(d, bx, y + 18, text, font(SANS, 14), bw3, 18, 3)
    y += 66
    d.line([M, y, W - M, y], fill=INK, width=1)
    y += 10

    # ---- Footer
    foot_f = font(SANS, 12)
    _, fh = draw_para(d, M, y, FOOTER, foot_f, CW, 16, 2, fill=GREY)
    y += fh + 6
    assert y <= H - 12, f"page overflow: content ends at y={y}"
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = draw_page()
    assert img.size == (W, H)
    img.save(out, "PNG")
    print(f"wrote {out} {img.size}")


if __name__ == "__main__":
    main()
