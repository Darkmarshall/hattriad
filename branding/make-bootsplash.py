#!/usr/bin/env python3
"""Replace the Debian boot-menu picture with the HatTriad one (three hats traced in blue line)."""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = sys.argv[1] if len(sys.argv) > 1 else "config/bootloaders"
W, H, SS = 640, 480, 3                      # the boot menu picture is 640x480
NAVY, BLUE = (11, 11, 30), (77, 163, 255)
WHITE, MUTED = (237, 235, 255), (184, 181, 222)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
HATS = [(100, 62), (58, 132), (142, 132)]   # hat centres, top-left corner like the old logo
SCALE = 0.5

def bezier(p0, p1, p2, p3, n=20):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                    u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    return out

def quad(p0, p1, p2, n=8):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]) for t in [i/n for i in range(n + 1)]]

def hat_paths():
    ts = [i * math.pi / 24 for i in range(25)]
    brim = [(70*math.cos(a), 34 + 16*math.sin(a)) for a in [i * 2*math.pi/72 for i in range(73)]]
    crown = (bezier((-40, 30), (-44, -6), (-32, -34), (-8, -32)) + quad((-8, -32), (0, -24), (8, -32))
             + bezier((8, -32), (32, -34), (44, -6), (40, 30)) + [(40*math.cos(a), 30 + 10*math.sin(a)) for a in ts])
    band = [(-41*math.cos(a), 14 + 10*math.sin(a)) for a in ts]
    return [brim, crown, band]

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()

def make_splash():
    img = Image.new("RGB", (W*SS, H*SS), NAVY)
    d = ImageDraw.Draw(img)
    for cx, cy in HATS:
        for p in hat_paths():
            xy = [((cx + x*SCALE) * SS, (cy + y*SCALE) * SS) for x, y in p]
            d.line(xy, fill=BLUE, width=int(2.2 * SS), joint="curve")
    img = img.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    d.text((190, 36), "HatTriad", font=font(FONT_B, 40), fill=WHITE)
    d.text((192, 92), "0.1 (experimental)", font=font(FONT_R, 18), fill=BLUE)
    d.text((192, 128), "based on Debian GNU/Linux 13 (trixie)", font=font(FONT_R, 13), fill=MUTED)
    return img

img = make_splash()
if ROOT.endswith('.png'):
    img.save(ROOT)
    print('wrote', ROOT)
    sys.exit(0)
done = 0
for dirpath, dirs, files in os.walk(ROOT):
    svgs = [f for f in files if f.startswith("splash.svg")]
    if svgs or "splash.png" in files:
        for f in svgs:
            os.remove(os.path.join(dirpath, f))
        img.save(os.path.join(dirpath, "splash.png"))
        print("splash.png written in", dirpath)
        done += 1
    if "theme.txt" in files:
        print("GRUB theme found in", dirpath, "->", sorted(f for f in files if f.endswith((".png", ".svg"))))
print(f"{done} bootloader folders updated")
