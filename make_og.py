#!/usr/bin/env python3
"""Generate a 1200x630 Open Graph preview card for the bridesmaid site."""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
SS = 2  # supersample for crisp text
img = Image.new("RGB", (W * SS, H * SS), (33, 16, 8))
d = ImageDraw.Draw(img, "RGBA")

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# --- warm vertical gradient (coffee -> deep wine -> coffee) ---
top = (42, 21, 9)
mid = (58, 14, 26)
bot = (33, 16, 8)
for y in range(H * SS):
    t = y / (H * SS)
    c = lerp(top, mid, t * 2) if t < 0.5 else lerp(mid, bot, (t - 0.5) * 2)
    d.line([(0, y), (W * SS, y)], fill=c)

# --- soft orange radial glow, top center ---
glow = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
cx, cy = int(W * SS * 0.5), int(H * SS * 0.08)
maxr = int(W * SS * 0.55)
for r in range(maxr, 0, -6):
    a = int(60 * (1 - r / maxr) ** 2)
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(210, 118, 47, a))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")

# --- scattered petals ---
PETALS = [(210, 118, 47), (237, 160, 97), (231, 196, 140), (154, 50, 71), (231, 183, 166)]
def petal(cx, cy, size, ang, color, alpha):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    s = size * SS
    pts = []
    for i in range(0, 361, 12):
        th = math.radians(i)
        # teardrop-ish petal
        rr = s * (0.5 + 0.5 * math.sin(th)) * (1 - 0.35 * math.cos(2 * th))
        pts.append((cx * SS + rr * math.cos(th + ang), cy * SS + rr * math.sin(th + ang)))
    ld.polygon(pts, fill=color + (alpha,))
    return layer

import random
random.seed(7)
for _ in range(26):
    px = random.randint(20, W - 20)
    py = random.randint(10, H - 10)
    sz = random.randint(7, 16)
    col = random.choice(PETALS)
    al = random.randint(45, 115)
    img = Image.alpha_composite(img.convert("RGBA"), petal(px, py, sz, random.uniform(0, 6.28), col, al)).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")

# --- fonts ---
def F(path, size, index=0):
    return ImageFont.truetype(path, size * SS, index=index)

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
SNELL = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"
FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"

f_eyebrow = F(FUTURA, 24)
f_names = F(SNELL, 60)
f_q = F(DIDOT, 92)
f_seal = F(DIDOT, 30)

GOLD = (231, 196, 140)
ORANGE = (237, 160, 97)
BLUSH = (231, 183, 166)
CREAM = (245, 231, 210)

def center_text(y, text, font, fill, tracking=0):
    # measure with tracking
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * SS * (len(text) - 1)
    x = (W * SS - total) / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + tracking * SS
    return total

# --- eyebrow ---
center_text(int(0.20 * H * SS), "YOU'RE INVITED", f_eyebrow, ORANGE, tracking=10)

# --- wax seal ---
scx, scy, sr = W * SS // 2, int(0.375 * H * SS), 52 * SS
d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=(110, 29, 46))
d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], outline=GOLD, width=2 * SS)
sb = d.textbbox((0, 0), "A&A", font=f_seal)
d.text((scx - (sb[2] - sb[0]) / 2, scy - (sb[3] - sb[1]) / 2 - sb[1]), "A&A", font=f_seal, fill=GOLD)

# --- names (script) ---
nb = d.textbbox((0, 0), "Adwoa & Abeiku", font=f_names)
center_text(int(0.50 * H * SS), "Adwoa & Abeiku", f_names, BLUSH)

# --- the question (gilded) ---
center_text(int(0.66 * H * SS), "Will you be my bridesmaid?", f_q, GOLD)

# --- downsample ---
final = img.resize((W, H), Image.LANCZOS)
final.save("/Users/pawuku/Documents/briidesmaid/og-image.png", "PNG")
print("saved og-image.png", final.size)
