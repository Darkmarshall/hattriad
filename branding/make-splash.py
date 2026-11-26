#!/usr/bin/env python3
"""Draw the HatTriad boot splash: three hats traced in blue line, frame by frame."""
import math, os, sys
from PIL import Image, ImageDraw

OUT = sys.argv[1] if len(sys.argv) > 1 else "splash"
N = 24                                          # frames 0..N (0 = empty, N = complete)
W, H = 640, 520                                 # canvas size in pixels
SS = 3                                          # supersampling, for smooth lines
BLUE = (77, 163, 255, 255)
LINE = 5                                        # line width in pixels
HATS = [(320, 130), (175, 360), (465, 360)]     # hat centres, forming a triangle
SCALE = 1.4

def bezier(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        pts.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                    u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    return pts

def quad(p0, p1, p2, n=10):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]) for t in [i/n for i in range(n + 1)]]

def hat_paths():
    ts = [i * math.pi / 24 for i in range(25)]
    brim = [(70*math.cos(a), 34 + 16*math.sin(a)) for a in [i * 2*math.pi/72 for i in range(73)]]
    crown = (bezier((-40, 30), (-44, -6), (-32, -34), (-8, -32)) + quad((-8, -32), (0, -24), (8, -32))
             + bezier((8, -32), (32, -34), (44, -6), (40, 30)) + [(40*math.cos(a), 30 + 10*math.sin(a)) for a in ts])
    band = [(-41*math.cos(a), 14 + 10*math.sin(a)) for a in ts]
    return [brim, crown, band]

def seglen(a, b): return math.hypot(b[0] - a[0], b[1] - a[1])

def frame(f):
    img = Image.new("RGBA", (W*SS, H*SS), (0, 0, 0, 0))
    if f <= 0:
        return img.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    paths = hat_paths()
    total = sum(seglen(p[i], p[i+1]) for p in paths for i in range(len(p) - 1))
    for cx, cy in HATS:
        left = f * total
        for p in paths:
            pts = [p[0]]
            for i in range(len(p) - 1):
                l = seglen(p[i], p[i+1])
                if left >= l:
                    pts.append(p[i+1]); left -= l
                else:
                    k = left / l if l else 0
                    pts.append((p[i][0] + (p[i+1][0]-p[i][0])*k, p[i][1] + (p[i+1][1]-p[i][1])*k))
                    left = 0
                    break
            if len(pts) > 1:
                xy = [((cx + x*SCALE) * SS, (cy + y*SCALE) * SS) for x, y in pts]
                d.line(xy, fill=BLUE, width=LINE*SS, joint="curve")
                r = LINE*SS/2
                for x, y in (xy[0], xy[-1]):
                    d.ellipse([x-r, y-r, x+r, y+r], fill=BLUE)
            if left <= 0:
                break
    return img.resize((W, H), Image.LANCZOS)

os.makedirs(OUT, exist_ok=True)
for i in range(N + 1):
    frame(i / N).save(os.path.join(OUT, f"hats-{i}.png"))
print(f"wrote {N + 1} frames to {OUT}")
