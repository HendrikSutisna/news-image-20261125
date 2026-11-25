#!/usr/bin/env python3
"""Build the WORLD NEWS front page for Wednesday 25 November 2026.

Fresh artwork for the make.fun news-image-20261125 bounty. All text is drawn
with real DejaVu fonts (PIL) so every letter renders cleanly; all pictures are
simple flat pictograms drawn with PIL shapes. Output: 1024x1024 PNG.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)      # cream newsprint
INK = (20, 20, 20)
RED = (176, 0, 32)
BLUE = (31, 78, 121)
GREEN = (30, 107, 52)
NAVY = (31, 42, 68)
GOLD = (255, 201, 60)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def text_w(s, f):
    return d.textlength(s, font=f)


def wrap(s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(lines, f, max_w, start_size):
    """Return (font, lines) with size lowered until every line fits."""
    size = start_size
    while size > 10:
        ff = SANS_B(size) if f == "b" else SANS(size)
        if all(text_w(ln, ff) <= max_w for ln in lines):
            return ff, lines
        size -= 2
    return SANS_B(10), lines


def hline(y, color, width, x0=8, x1=1016):
    d.rectangle([x0, y, x1, y + width - 1], fill=color)


# ---- outer frame ------------------------------------------------------------
d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=8)

# ---- masthead ---------------------------------------------------------------
d.rectangle([8, 8, 1016, 108], fill=INK)
mast = SERIF_B(86)
d.text((512, 58), "WORLD NEWS", font=mast, fill=(255, 255, 255), anchor="mm")
hline(108, RED, 6)

# ---- dateline ---------------------------------------------------------------
date_f = SANS_B(27)
date_s = "W E D N E S D A Y   2 5   N O V E M B E R   2 0 2 6"
d.text((512, 136), date_s, font=date_f, fill=INK, anchor="mm")
hline(158, INK, 3)

# ---- lead panel -------------------------------------------------------------
LY0, LY1 = 170, 392
d.rectangle([8, LY0, 1016, LY1], outline=INK, width=2)
hline(LY0, RED, 4)
d.text((24, 182), "YEMEN", font=SANS_B(24), fill=RED)
lead_head = ["SAUDI JETS BOMB HODEIDAH", "PORT AS WAR WIDENS"]
lf, _ = fit_lines(lead_head, "b", 672, 46)
y = 214
for ln in lead_head:
    d.text((24, y), ln, font=lf, fill=INK)
    y += lf.size + 6
lead_body = wrap(
    "Coalition strikes Houthi-held Hodeidah port and targets in Saada "
    "and Amran; Houthis threaten Jeddah.",
    SANS(24), 672)
by = 322
for ln in lead_body:
    d.text((24, by), ln, font=SANS(24), fill=INK)
    by += 30

# lead art: Hodeidah port under fire
AX0, AY0, AX1, AY1 = 712, 180, 1000, 382
d.rectangle([AX0, AY0, AX1, AY1], fill=NAVY)
d.text((AX0 + 10, AY0 + 8), "HODEIDAH UNDER FIRE", font=SANS_B(19), fill=(255, 255, 255))
# sea
d.rectangle([AX0, AY1 - 42, AX1, AY1], fill=(38, 68, 110))
for i, wx in enumerate(range(AX0 + 6, AX1 - 10, 26)):
    d.arc([wx, AY1 - 30, wx + 22, AY1 - 12], 0, 180, fill=(150, 190, 230), width=3)
# ship hull
d.polygon([(AX0 + 22, AY1 - 88), (AX1 - 22, AY1 - 88), (AX1 - 48, AY1 - 42),
           (AX0 + 48, AY1 - 42)], fill=(178, 44, 36))
# containers
d.rectangle([AX0 + 46, AY1 - 128, AX0 + 106, AY1 - 88], fill=(240, 200, 60))
d.rectangle([AX0 + 112, AY1 - 118, AX0 + 168, AY1 - 88], fill=(90, 180, 110))
d.rectangle([AX0 + 174, AY1 - 128, AX0 + 226, AY1 - 88], fill=(200, 200, 200))
# funnel
d.rectangle([AX0 + 232, AY1 - 138, AX0 + 258, AY1 - 88], fill=(120, 120, 120))
# flames
for cx, cy, r in [(AX0 + 76, AY1 - 140, 16), (AX0 + 140, AY1 - 132, 20),
                  (AX0 + 205, AY1 - 142, 15)]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 140, 0))
    d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=(255, 220, 80))
# mine in the water
mx, my = AX0 + 60, AY1 - 22
d.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=INK)
for ang in range(0, 360, 45):
    import math
    x1 = mx + 11 * math.cos(math.radians(ang))
    y1 = my + 11 * math.sin(math.radians(ang))
    x2 = mx + 18 * math.cos(math.radians(ang))
    y2 = my + 18 * math.sin(math.radians(ang))
    d.line([x1, y1, x2, y2], fill=INK, width=3)

# ---- small panels -----------------------------------------------------------
def fit_head(head_lines, max_widths, start_size):
    """Headline font sized so each line fits its own max width.

    Line 1 shares its row with the pictogram, so it gets the narrower
    width; later lines get the full panel width.
    """
    size = start_size
    while size > 10:
        ff = SANS_B(size)
        if all(text_w(ln, ff) <= mw for ln, mw in zip(head_lines, max_widths)):
            return ff
        size -= 2
    return SANS_B(10)


def small_panel(x0, x1, y0, y1, rule_color, kicker, head_lines, body, icon):
    d.rectangle([x0, y0, x1, y1], outline=INK, width=2)
    hline(y0, rule_color, 4, x0, x1)
    d.text((x0 + 16, y0 + 14), kicker, font=SANS_B(22), fill=rule_color)
    full_w = x1 - x0 - 32
    widths = [full_w - 78] + [full_w] * (len(head_lines) - 1)
    hf = fit_head(head_lines, widths, 34)
    y = y0 + 46
    for ln in head_lines:
        d.text((x0 + 16, y), ln, font=hf, fill=INK)
        y += hf.size + 4
    bf = SANS(21)
    for ln in wrap(body, bf, full_w):
        d.text((x0 + 16, y), ln, font=bf, fill=INK)
        y += 27
    icon(x1 - 78, y0 + 12)


def icon_treaty(ix, iy):
    d.rectangle([ix, iy, ix + 62, iy + 62], outline=INK, width=2, fill=(239, 232, 216))
    d.rectangle([ix + 12, iy + 10, ix + 50, iy + 46], fill=(255, 255, 255), outline=INK)
    for j, yy in enumerate(range(iy + 16, iy + 40, 8)):
        d.line([ix + 17, yy, ix + 45, yy], fill=(120, 120, 120), width=2)
    d.ellipse([ix + 36, iy + 38, ix + 52, iy + 54], fill=RED, outline=(255, 255, 255))
    d.line([ix + 8, iy + 52, ix + 30, iy + 30], fill=BLUE, width=3)


def icon_store(ix, iy):
    d.rectangle([ix, iy, ix + 62, iy + 62], outline=INK, width=2, fill=(239, 232, 216))
    d.rectangle([ix + 10, iy + 22, ix + 52, iy + 54], fill=(200, 210, 225), outline=INK)
    for j in range(4):
        x = ix + 10 + j * 11
        d.rectangle([x, iy + 12, x + 11, iy + 22], fill=RED if j % 2 == 0 else (255, 255, 255),
                    outline=INK)
    d.rectangle([ix + 26, iy + 38, ix + 36, iy + 54], fill=INK)
    d.ellipse([ix + 40, iy + 6, ix + 58, iy + 24], fill=GOLD, outline=INK)
    d.text((ix + 49, iy + 15), "*", font=SANS_B(18), fill=INK, anchor="mm")


def icon_coins(ix, iy):
    d.rectangle([ix, iy, ix + 62, iy + 62], outline=INK, width=2, fill=(239, 232, 216))
    for j, yy in enumerate([iy + 42, iy + 32, iy + 22]):
        d.ellipse([ix + 12, yy, ix + 34, yy + 12], fill=GOLD, outline=INK)
        d.text((ix + 23, yy + 6), "$", font=SANS_B(11), fill=INK, anchor="mm")
    d.line([ix + 44, iy + 48, ix + 44, iy + 16], fill=GREEN, width=4)
    d.polygon([(ix + 36, iy + 22), (ix + 44, iy + 10), (ix + 52, iy + 22)], fill=GREEN)


def icon_mine(ix, iy):
    d.rectangle([ix, iy, ix + 62, iy + 62], outline=INK, width=2, fill=(239, 232, 216))
    d.pieslice([ix + 14, iy + 14, ix + 48, iy + 56], 180, 360, fill=(60, 60, 60))
    d.rectangle([ix + 14, iy + 40, ix + 48, iy + 56], fill=(60, 60, 60))
    d.arc([ix + 22, iy + 30, ix + 40, iy + 48], 180, 360, fill=GOLD, width=3)
    d.ellipse([ix + 29, iy + 26, ix + 33, iy + 30], fill=GOLD)
    for wx in range(ix + 6, ix + 56, 10):
        d.arc([wx, iy + 50, wx + 10, iy + 60], 0, 180, fill=BLUE, width=2)


R2Y0, R2Y1 = 404, 612
R3Y0, R3Y1 = 624, 832
small_panel(8, 505, R2Y0, R2Y1, BLUE, "PACIFIC",
            ["SOLOMONS PICK AUSTRALIA", "IN HISTORIC TREATY"],
            "Albanese and Wale sign in Canberra; Solomons rule out any "
            "foreign military base on their soil.",
            icon_treaty)
small_panel(519, 1016, R2Y0, R2Y1, RED, "COLOMBIA",
            ["ALL HOSTAGES FREED", "IN CARTAGENA RAID"],
            "Troops storm supermarket after day-long siege; one gunman "
            "killed, four detained.",
            icon_store)
small_panel(8, 505, R3Y0, R3Y1, GREEN, "BANGLADESH",
            ["GARMENT PAY UP 36%", "AFTER PROTESTS"],
            "Minimum wage rises to Tk17,000 a month from Tk12,500; board "
            "votes 4-2 after weeks of strikes.",
            icon_coins)
small_panel(519, 1016, R3Y0, R3Y1, BLUE, "INDONESIA",
            ["3 DEAD, 23 STILL TRAPPED", "IN FLOODED MINE"],
            "Rescuers pump water from 100m shaft at illegal gold mine in "
            "Bogor; 11 miners escaped Monday.",
            icon_mine)

# ---- bottom strip -----------------------------------------------------------
SY0, SY1 = 844, 1008
d.rectangle([8, SY0, 1016, SY1], fill=NAVY)
strip = [
    "North Korea expels Swiss envoy \u2014 48 hours to leave.",
    "Houthis advance on Aden as residents prepare to flee.",
    "Nikkei falls 2.8% as AI doubts hit tech shares.",
]
sy = SY0 + 16
d.text((24, sy), "ALSO:", font=SANS_B(24), fill=GOLD)
sx = 24 + text_w("ALSO:  ", SANS_B(24))
for ln in strip:
    d.text((sx, sy), ln, font=SANS(23), fill=(255, 255, 255))
    sy += 32
d.text((24, SY1 - 30), "WORLD NEWS  \u00b7  25 NOVEMBER 2026",
       font=SANS_B(16), fill=(150, 170, 200))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "entry.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out, optimize=True)
print("saved", out, os.path.getsize(out), "bytes")
