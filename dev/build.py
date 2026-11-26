#!/usr/bin/env python3
"""Draw the WORLD NEWS front page for Wednesday 25 November 2026, v2.

Self-contained Pillow renderer: every glyph, rule and picture on the page
is drawn from the story data below with plain drawing primitives, so the
output is byte-for-byte deterministic. Usage:

    python3 dev/build.py [output.png]

Default output is entry/entry.png next to the repository root.
"""

from __future__ import annotations

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (18, 18, 18)
RED = (193, 39, 45)
NAVY = (28, 43, 74)
NAVY_DEEP = (23, 35, 60)
SEA_DARK = (18, 32, 56)
GOLD = (245, 179, 1)
GREEN = (30, 125, 50)
BLUE = (21, 101, 192)
SEA = (52, 96, 140)
MUTED = (158, 175, 208)
WHITE = (255, 255, 255)
ICON_BG = (238, 232, 214)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MASTHEAD_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

MASTHEAD = "WORLD NEWS"
DATELINE = "WEDNESDAY 25 NOVEMBER 2026"

LEAD = {
    "kicker": "YEMEN",
    "headline": "SAUDI JETS BOMB HODEIDAH PORT AS WAR WIDENS",
    "summary": (
        "Coalition strikes Houthi-held Hodeidah port and targets in Saada "
        "and Amran; Houthis claim a hit on Ras Tanura refinery and threaten Jeddah."
    ),
}

PANELS = [
    {
        "kicker": "PACIFIC",
        "color": BLUE,
        "headline": "SOLOMONS PICK AUSTRALIA IN HISTORIC TREATY",
        "summary": (
            "Albanese and Wale sign in Canberra; Solomons rule out any "
            "foreign military base on their soil."
        ),
        "icon": "treaty",
    },
    {
        "kicker": "COLOMBIA",
        "color": RED,
        "headline": "ALL HOSTAGES FREED IN CARTAGENA RAID",
        "summary": (
            "Troops storm supermarket after day-long siege; one gunman "
            "killed, four detained."
        ),
        "icon": "store",
    },
    {
        "kicker": "BANGLADESH",
        "color": GREEN,
        "headline": "GARMENT PAY UP 36% AFTER PROTESTS",
        "summary": (
            "Minimum wage rises to Tk17,000 a month from Tk12,500; board "
            "votes 4-2 after weeks of strikes."
        ),
        "icon": "coins",
    },
    {
        "kicker": "INDONESIA",
        "color": BLUE,
        "headline": "9 DEAD, 17 STILL TRAPPED IN FLOODED MINE",
        "summary": (
            "Rescuers pump water from 100m shaft at illegal gold mine in "
            "Bogor; 11 miners escaped Monday."
        ),
        "icon": "mine",
    },
]

STRIP = [
    "North Korea expels Swiss envoy \u2014 48 hours to leave.",
    "Pakistan's first astronaut docks at Tiangong aboard Shenzhou-24.",
    "Nikkei falls 2.8% as AI doubts hit tech shares.",
]

FOOTER = "WORLD NEWS \u00b7 25 NOVEMBER 2026"


def load(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; a single over-long word still goes on its own line."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_wrap(draw, text, path, size, max_w, max_lines, min_size=20):
    """Largest size (stepping down by 2) whose wrap fits max_lines lines."""
    while size >= min_size:
        font = load(path, size)
        lines = wrap(draw, text, font, max_w)
        if len(lines) <= max_lines and all(
            text_w(draw, line, font) <= max_w for line in lines
        ):
            return font, lines
        size -= 2
    font = load(path, min_size)
    return font, wrap(draw, text, font, max_w)


def tracked_width(draw, text, font, track):
    total = sum(text_w(draw, ch, font) for ch in text)
    return total + track * max(len(text) - 1, 0)


def draw_tracked(draw, cx, y, text, font, fill, track):
    x = cx - tracked_width(draw, text, font, track) / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += text_w(draw, ch, font) + track


# ---------------------------------------------------------------- icons


def icon_box(draw, px, py):
    draw.rectangle([px, py, px + 64, py + 64], fill=ICON_BG, outline=INK, width=2)


def icon_treaty(draw, px, py):
    icon_box(draw, px, py)
    draw.rectangle([px + 14, py + 10, px + 42, py + 52], fill=WHITE, outline=INK, width=2)
    draw.polygon(
        [(px + 42, py + 10), (px + 52, py + 20), (px + 42, py + 20)],
        fill=(205, 205, 205),
    )
    for ly in (22, 30, 38):
        draw.line([px + 19, py + ly, px + 37, py + ly], fill=(130, 130, 130), width=2)
    draw.line([px + 12, py + 54, px + 48, py + 20], fill=BLUE, width=4)
    draw.ellipse([px + 44, py + 44, px + 58, py + 58], fill=RED)


def icon_store(draw, px, py):
    icon_box(draw, px, py)
    for i in range(5):
        colour = RED if i % 2 == 0 else WHITE
        draw.rectangle(
            [px + 10 + i * 9, py + 12, px + 18 + i * 9, py + 24],
            fill=colour,
            outline=INK,
        )
    draw.rectangle([px + 12, py + 24, px + 52, py + 52], fill=(212, 212, 212), outline=INK, width=2)
    draw.rectangle([px + 26, py + 34, px + 38, py + 52], fill=NAVY)
    draw.ellipse([px + 46, py + 8, px + 58, py + 20], fill=GOLD, outline=INK)


def icon_coins(draw, px, py):
    icon_box(draw, px, py)
    for cx, cy in ((px + 24, py + 44), (px + 38, py + 44), (px + 31, py + 30)):
        draw.ellipse([cx - 10, cy - 8, cx + 10, cy + 8], fill=(232, 178, 32), outline=(150, 110, 10), width=2)
        draw.text((cx - 3, cy - 7), "$", font=load(SANS_BOLD, 12), fill=(120, 80, 0))
    draw.line([px + 46, py + 50, px + 56, py + 18], fill=GREEN, width=4)
    draw.polygon([(px + 56, py + 12), (px + 50, py + 22), (px + 60, py + 22)], fill=GREEN)


def icon_mine(draw, px, py):
    icon_box(draw, px, py)
    draw.pieslice([px + 14, py + 14, px + 50, py + 50], 180, 360, fill=(40, 40, 40))
    draw.rectangle([px + 14, py + 32, px + 50, py + 50], fill=(40, 40, 40))
    draw.arc([px + 24, py + 26, px + 40, py + 40], 180, 360, fill=GOLD, width=4)
    draw.line([px + 20, py + 40, px + 44, py + 40], fill=GOLD, width=3)
    for wx in (px + 10, px + 26, px + 42):
        draw.arc([wx, py + 52, wx + 16, py + 60], 180, 360, fill=SEA, width=2)


ICONS = {
    "treaty": icon_treaty,
    "store": icon_store,
    "coins": icon_coins,
    "mine": icon_mine,
}


def draw_ship(draw, x, y, w, h):
    """Lead illustration: cargo ship under fire at Hodeidah port."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    draw.text((x + 14, y + 10), "HODEIDAH UNDER FIRE", font=load(SANS_BOLD, 20), fill=WHITE)
    draw.rectangle([x + 36, y + 104, x + 100, y + 150], fill=(232, 178, 32))
    draw.rectangle([x + 112, y + 96, x + 176, y + 150], fill=(46, 160, 90))
    draw.rectangle([x + 188, y + 104, x + 252, y + 150], fill=(168, 172, 176))
    draw.rectangle([x + 264, y + 112, x + 304, y + 150], fill=(120, 124, 128))
    for cx, cy in ((x + 68, y + 88), (x + 144, y + 80), (x + 220, y + 88)):
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(240, 120, 20))
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(250, 210, 60))
    draw.polygon(
        [(x + 16, y + 150), (x + 320, y + 150), (x + 292, y + 196), (x + 44, y + 196)],
        fill=(198, 52, 40),
    )
    draw.rectangle([x, y + 196, x + w, y + h], fill=SEA_DARK)
    for wx in range(x + 8, x + w - 24, 28):
        draw.arc([wx, y + 202, wx + 24, y + 212], 180, 360, fill=SEA, width=2)
    mx, my = x + 44, y + 200
    for dx, dy in ((-9, -9), (0, -12), (9, -9), (-12, 0), (12, 0), (-9, 9), (9, 9)):
        draw.line([mx, my, mx + dx, my + dy], fill=INK, width=2)
    draw.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=INK)


# ---------------------------------------------------------------- layout


def draw_masthead(draw):
    draw.rectangle([0, 0, W, 104], fill=INK)
    size = 96
    while size > 60:
        font = load(MASTHEAD_FONT, size)
        if text_w(draw, MASTHEAD, font) <= 940:
            break
        size -= 2
    font = load(MASTHEAD_FONT, size)
    tw = text_w(draw, MASTHEAD, font)
    draw.text(((W - tw) / 2, (104 - size) / 2 - 4), MASTHEAD, font=font, fill=WHITE)
    draw.rectangle([0, 104, W, 110], fill=RED)
    draw.line([0, 112, W, 112], fill=INK, width=2)
    draw_tracked(draw, W / 2, 118, DATELINE, load(SANS_BOLD, 27), INK, 12)
    draw.line([0, 154, W, 154], fill=INK, width=2)
    draw.rectangle([0, 156, W, 161], fill=RED)


def draw_lead(draw, x, y, w, h):
    draw.text((x + 24, y + 14), LEAD["kicker"], font=load(SANS_BOLD, 24), fill=RED)
    head_f, head_lines = fit_wrap(draw, LEAD["headline"], SERIF_BOLD, 46, 624, 2, min_size=36)
    hy = y + 48
    for line in head_lines:
        draw.text((x + 24, hy), line, font=head_f, fill=INK)
        hy += head_f.size + 6
    sum_f = load(SANS, 21)
    sy = hy + 8
    for line in wrap(draw, LEAD["summary"], sum_f, 624)[:3]:
        draw.text((x + 24, sy), line, font=sum_f, fill=INK)
        sy += 27
    draw_ship(draw, x + 664, y + 14, 336, 216)


def draw_panel(draw, x, y, w, h, story):
    draw.text((x + 22, y + 14), story["kicker"], font=load(SANS_BOLD, 22), fill=story["color"])
    ICONS[story["icon"]](draw, x + w - 86, y + 12)
    head_f, head_lines = fit_wrap(draw, story["headline"], SERIF_BOLD, 28, w - 44 - 84, 2, min_size=22)
    hy = y + 46
    for line in head_lines:
        draw.text((x + 22, hy), line, font=head_f, fill=INK)
        hy += head_f.size + 6
    sum_f = load(SANS, 19)
    sy = hy + 6
    for line in wrap(draw, story["summary"], sum_f, w - 44)[:3]:
        draw.text((x + 22, sy), line, font=sum_f, fill=INK)
        sy += 25


def draw_strip(draw, y, h):
    draw.rectangle([0, y, W, y + h], fill=NAVY_DEEP)
    draw.text((24, y + 12), "ALSO:", font=load(SANS_BOLD, 22), fill=GOLD)
    line_f = load(SANS, 20)
    ly = y + 12
    for line in STRIP:
        draw.text((120, ly), line, font=line_f, fill=WHITE)
        ly += 24


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_lead(draw, 0, 161, W, 246)
    draw.line([0, 407, W, 407], fill=INK, width=3)
    draw_panel(draw, 0, 410, 512, 244, PANELS[0])
    draw_panel(draw, 512, 410, 512, 244, PANELS[1])
    draw_panel(draw, 0, 654, 512, 244, PANELS[2])
    draw_panel(draw, 512, 654, 512, 244, PANELS[3])
    draw.line([512, 410, 512, 898], fill=INK, width=3)
    draw.line([0, 654, W, 654], fill=INK, width=3)
    draw_strip(draw, 898, 86)
    draw.rectangle([0, 984, W, H], fill=INK)
    draw.text((24, 1000), FOOTER, font=load(SANS, 16), fill=MUTED)
    draw.rectangle([0, 0, W - 1, H - 1], outline=INK, width=5)
    return img


def main(argv):
    if len(argv) > 1:
        out = argv[1]
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        out = os.path.normpath(os.path.join(here, "..", "entry", "entry.png"))
    img = build()
    if img.size != (W, H):
        raise SystemExit(f"bad size {img.size}")
    img.save(out, format="PNG")
    with open(out, "rb") as fh:
        data = fh.read()
    print(f"wrote {out} {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
