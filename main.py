#!/usr/bin/env python3
"""ai-excited-01 — "Make the AI judge excited"
Golden koi leaps from a teacup toward the moon.
Pure Python 3 stdlib, no external dependencies.
Deterministic: fixed seeds, no timestamps, no randomness without seed.
Writes a 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Scene: night sky, glowing moon top-right, a golden koi arcing from a
steaming teacup (bottom-left) up toward the moon, bold caption top-left:
"TOO BIG FOR THE CUP. SHE JUMPED ANYWAY."
"""
import math
import os
import random
import struct
import zlib

W = 1024
S = 2  # supersample factor for smooth edges
PW = W * S
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

buf = bytearray(PW * PW * 3)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return (round(lerp(c1[0], c2[0], t)),
            round(lerp(c1[1], c2[1], t)),
            round(lerp(c1[2], c2[2], t)))


def _span(y, x0, x1, rgb):
    """Fill one supersampled row from x0..x1 inclusive (SS coords)."""
    if y < 0 or y >= PW:
        return
    x0 = max(0, x0)
    x1 = min(PW - 1, x1)
    if x1 < x0:
        return
    n = x1 - x0 + 1
    base = (y * PW + x0) * 3
    buf[base:base + n * 3] = bytes(rgb) * n


def _blend_px(x, y, rgb, a):
    if x < 0 or x >= PW or y < 0 or y >= PW:
        return
    i = (y * PW + x) * 3
    buf[i] = round(buf[i] * (1.0 - a) + rgb[0] * a)
    buf[i + 1] = round(buf[i + 1] * (1.0 - a) + rgb[1] * a)
    buf[i + 2] = round(buf[i + 2] * (1.0 - a) + rgb[2] * a)


def fill_circle(cx, cy, r, rgb, alpha=1.0):
    """Filled circle, coords in 1024 space. Alpha blends if < 1."""
    cx, cy, r = cx * S, cy * S, r * S
    y0, y1 = int(cy - r), int(cy + r) + 1
    r2 = r * r
    for y in range(y0, y1):
        dy = y - cy
        rem = r2 - dy * dy
        if rem < 0:
            continue
        dx = int(math.sqrt(rem))
        if alpha >= 1.0:
            _span(y, int(cx - dx), int(cx + dx), rgb)
        else:
            for x in range(int(cx - dx), int(cx + dx) + 1):
                _blend_px(x, y, rgb, alpha)


def fill_ellipse(cx, cy, rx, ry, rgb, alpha=1.0):
    cx, cy, rx, ry = cx * S, cy * S, rx * S, ry * S
    y0, y1 = int(cy - ry), int(cy + ry) + 1
    for y in range(y0, y1):
        dy = (y - cy) / ry
        rem = 1.0 - dy * dy
        if rem < 0:
            continue
        dx = int(rx * math.sqrt(rem))
        if alpha >= 1.0:
            _span(y, int(cx - dx), int(cx + dx), rgb)
        else:
            for x in range(int(cx - dx), int(cx + dx) + 1):
                _blend_px(x, y, rgb, alpha)


def fill_polygon(points, rgb, alpha=1.0):
    """Even-odd scanline polygon fill, points in 1024 space."""
    pts = [(x * S, y * S) for x, y in points]
    ys = [p[1] for p in pts]
    y0, y1 = int(min(ys)), int(max(ys)) + 1
    n = len(pts)
    for y in range(y0, y1):
        xs = []
        for i in range(n):
            x1, y1p = pts[i]
            x2, y2p = pts[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                xs.append(x1 + (y - y1p) * (x2 - x1) / (y2p - y1p))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            xa, xb = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
            if alpha >= 1.0:
                _span(y, xa, xb, rgb)
            else:
                for x in range(xa, xb + 1):
                    _blend_px(x, y, rgb, alpha)


def draw_sky():
    """Vertical dusk gradient + stars."""
    stops = [
        (0, (9, 15, 46)),
        (280, (22, 36, 82)),
        (540, (58, 58, 108)),
        (680, (128, 66, 76)),
        (780, (96, 52, 62)),
    ]
    row_rgb = []
    for y in range(PW):
        yy = y / S
        for i in range(len(stops) - 1):
            y_a, c_a = stops[i]
            y_b, c_b = stops[i + 1]
            if y_a <= yy <= y_b:
                t = (yy - y_a) / max(1.0, y_b - y_a)
                row_rgb.append(mix(c_a, c_b, t))
                break
        else:
            row_rgb.append(stops[-1][1])
    for y in range(PW):
        base = y * PW * 3
        buf[base:base + PW * 3] = bytes(row_rgb[y]) * PW
    # stars: fixed seed, deterministic
    rng = random.Random(7)
    for _ in range(150):
        x = rng.uniform(0, W)
        y = rng.uniform(0, 640)
        r = rng.uniform(0.6, 1.9)
        b = rng.uniform(0.45, 1.0)
        col = (round(255 * b), round(244 * b), round(214 * b))
        fill_circle(x, y, r, col, alpha=0.55 + 0.45 * b)
    # a few 4-point sparkles
    for _ in range(10):
        x = rng.uniform(40, 980)
        y = rng.uniform(30, 420)
        s = rng.uniform(3, 7)
        col = (255, 246, 210)
        fill_polygon([(x, y - s), (x + s * 0.28, y - s * 0.28),
                      (x + s, y), (x + s * 0.28, y + s * 0.28),
                      (x, y + s), (x - s * 0.28, y + s * 0.28),
                      (x - s, y), (x - s * 0.28, y - s * 0.28)], col, alpha=0.9)


def draw_moon():
    """Big glowing moon, top-right, with soft halo and craters."""
    cx, cy, r = 860, 250, 128
    # halo: radial falloff blended over the sky
    R = int(r * 1.9)
    for yy in range(int((cy - R) * S), int((cy + R) * S) + 1):
        dy = yy / S - cy
        for xx in range(int((cx - R) * S), int((cx + R) * S) + 1):
            dx = xx / S - cx
            d = math.hypot(dx, dy)
            if d >= R:
                continue
            t = 1.0 - d / R
            a = (t * t) * 0.55
            _blend_px(xx, yy, (245, 214, 122), a)
    fill_circle(cx, cy, r, (248, 232, 176))
    fill_circle(cx - 18, cy - 14, r - 6, (250, 238, 192))
    # craters
    for (ox, oy, cr, shade) in [
            (-42, -30, 17, (228, 202, 143)), (28, -52, 12, (228, 202, 143)),
            (52, 18, 20, (232, 208, 150)), (-8, 44, 14, (228, 202, 143)),
            (70, -18, 9, (232, 208, 150)), (-62, 34, 10, (232, 208, 150))]:
        fill_circle(cx + ox, cy + oy, cr, shade)
    # bright rim on the lower-left (light facing the koi)
    fill_circle(cx - 6, cy + 4, r - 14, (252, 242, 200), alpha=0.35)


def write_png(path):
    """Downsample 2x -> 1024x1024 and write a deterministic PNG."""
    raw = bytearray()
    for y in range(W):
        raw.append(0)  # filter: none
        sy = y * S
        for x in range(W):
            sx = x * S
            i00 = (sy * PW + sx) * 3
            i01 = i00 + 3
            i10 = ((sy + 1) * PW + sx) * 3
            i11 = i10 + 3
            raw.append((buf[i00] + buf[i01] + buf[i10] + buf[i11]) // 4)
            raw.append((buf[i00 + 1] + buf[i01 + 1] + buf[i10 + 1] + buf[i11 + 1]) // 4)
            raw.append((buf[i00 + 2] + buf[i01 + 2] + buf[i10 + 2] + buf[i11 + 2]) // 4)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, W, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------------------
# Scene part 2: tabletop, teacup, steam, splash, motion streaks
# ---------------------------------------------------------------------------

def draw_tabletop():
    """Warm dark wooden surface the cup sits on (y 780..1024)."""
    stops = [(780, (64, 42, 36)), (880, (48, 31, 28)), (1024, (28, 18, 20))]
    for y in range(int(780 * S), PW):
        yy = y / S
        for i in range(len(stops) - 1):
            y_a, c_a = stops[i]
            y_b, c_b = stops[i + 1]
            if y_a <= yy <= y_b:
                t = (yy - y_a) / max(1.0, y_b - y_a)
                _span(y, 0, PW - 1, mix(c_a, c_b, t))
                break
        else:
            _span(y, 0, PW - 1, stops[-1][1])
    # soft golden moonlight pool on the table under the moon
    for yy in range(int(800 * S), PW):
        dy = (yy / S - 800) / 224.0
        for xx in range(int(560 * S), int(1000 * S)):
            dx = (xx / S - 780) / 220.0
            d = math.hypot(dx, dy * 1.6)
            if d < 1.0:
                a = (1.0 - d) * 0.20 * (1.0 - dy * 0.6)
                _blend_px(xx, yy, (214, 164, 92), max(0.0, a))
    # faint wood-grain lines
    rng = random.Random(21)
    for _ in range(14):
        y = rng.uniform(800, 1010)
        x0 = rng.uniform(0, 300)
        x1 = rng.uniform(700, 1024)
        for x in range(int(x0), int(x1)):
            _blend_px(int(x * S), int(y * S), (90, 60, 48), 0.18)


def bezier(p0, p1, p2, n=64):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1.0 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def draw_teacup():
    """Cream porcelain cup with gold rim and red band, on a saucer."""
    cx = 300
    # soft shadow under saucer
    fill_ellipse(cx, 918, 168, 22, (12, 8, 10), alpha=0.55)
    # saucer
    fill_ellipse(cx, 905, 158, 26, (243, 230, 200))
    fill_ellipse(cx, 903, 158, 24, (247, 236, 210))
    fill_ellipse(cx, 903, 128, 18, (214, 178, 96))
    fill_ellipse(cx, 903, 118, 15, (243, 230, 200))
    # handle: thick arc on the right side of the cup
    for ang in range(-70, 75, 4):
        a = math.radians(ang)
        hx = cx + 92 + 34 * math.cos(a)
        hy = 845 + 30 * math.sin(a)
        fill_circle(hx, hy, 9, (240, 226, 194))
    for ang in range(-70, 75, 4):
        a = math.radians(ang)
        hx = cx + 92 + 34 * math.cos(a)
        hy = 845 + 30 * math.sin(a)
        fill_circle(hx, hy, 4.5, (58, 38, 34))
    # cup body (slightly tapered, rounded bottom)
    fill_polygon([(cx - 88, 798), (cx + 88, 798), (cx + 76, 878),
                  (cx + 58, 898), (cx - 58, 898), (cx - 76, 878)],
                 (243, 230, 200))
    fill_polygon([(cx - 88, 798), (cx + 88, 798), (cx + 84, 828),
                  (cx - 84, 828)], (250, 240, 216))
    # red + gold pattern band
    fill_polygon([(cx - 85, 836), (cx + 85, 836), (cx + 82, 858),
                  (cx - 82, 858)], (178, 58, 46))
    fill_polygon([(cx - 84, 858), (cx + 84, 858), (cx + 83, 864),
                  (cx - 83, 864)], (201, 151, 63))
    # small gold diamonds on the band
    for dx in (-56, -28, 0, 28, 56):
        fill_polygon([(cx + dx, 840), (cx + dx + 6, 847), (cx + dx, 854),
                      (cx + dx - 6, 847)], (247, 214, 130))
    # rim + tea surface
    fill_ellipse(cx, 798, 88, 17, (201, 151, 63))
    fill_ellipse(cx, 798, 82, 14, (247, 236, 210))
    fill_ellipse(cx, 798, 74, 11, (196, 118, 26))
    fill_ellipse(cx - 18, 796, 30, 4.5, (232, 164, 62))
    # highlight on the cup's left side
    fill_polygon([(cx - 78, 806), (cx - 62, 806), (cx - 66, 884),
                  (cx - 74, 884)], (252, 244, 224), alpha=0.5)


def draw_steam():
    """Two translucent steam curls rising from the tea."""
    rng = random.Random(33)
    for base_x, phase, amp in [(282, 0.0, 14), (322, 1.7, 18)]:
        for i in range(26):
            t = i / 25.0
            y = 786 - t * 150
            x = base_x + math.sin(t * 5.2 + phase) * amp * (0.4 + t)
            r = 4 + t * 10
            fill_circle(x, y, r, (255, 248, 230), alpha=0.11 * (1.0 - t * 0.55))
    # tiny rising sparkle in the steam
    for _ in range(8):
        x = rng.uniform(255, 350)
        y = rng.uniform(640, 770)
        fill_circle(x, y, rng.uniform(1.0, 2.2), (255, 240, 200), alpha=0.8)


def draw_splash():
    """Tea/water bursting out of the cup mouth where the koi left."""
    rng = random.Random(55)
    # splash crown at the cup mouth
    for i in range(9):
        t = i / 8.0
        ang = math.pi * (0.08 + 0.84 * t)
        x = 300 + math.cos(ang) * 62
        y = 792 - math.sin(ang) * (26 + 14 * math.sin(t * math.pi))
        fill_ellipse(x, y, 7 - 2 * abs(t - 0.5), 12, (214, 232, 240), alpha=0.9)
    # droplets arcing up after the fish
    arc = bezier((300, 780), (400, 400), (715, 305))
    for i, (x, y) in enumerate(arc):
        if i % 3 != 0:
            continue
        t = i / len(arc)
        for k in range(2):
            ox = rng.uniform(-46, -14)
            oy = rng.uniform(-8, 26)
            r = rng.uniform(2.0, 5.5) * (1.0 - t * 0.45)
            fill_circle(x + ox, y + oy, r, (206, 228, 242),
                        alpha=0.85 - t * 0.3)
    # big hero droplets near the cup, catching the light
    for (x, y, r) in [(238, 742, 9), (372, 730, 7), (262, 700, 6),
                      (348, 688, 8), (210, 786, 6)]:
        fill_circle(x, y, r, (222, 236, 246))
        fill_circle(x - r * 0.3, y - r * 0.3, r * 0.35, (255, 255, 255))


def draw_motion_streaks(arc):
    """Three pale-gold speed lines trailing behind the koi."""
    arc = bezier(*KOI_ARC, n=200)  # fine sampling so dots merge into lines
    for off, alpha in [(88, 0.45), (118, 0.32), (150, 0.22)]:
        pts = []
        for i, (x, y) in enumerate(arc):
            t = i / (len(arc) - 1)
            if t < 0.12 or t > 0.82:
                continue
            # outward normal of the curve
            j = min(i + 1, len(arc) - 1)
            dx, dy = arc[j][0] - arc[max(i - 1, 0)][0], arc[j][1] - arc[max(i - 1, 0)][1]
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L, dx / L
            pts.append((x + nx * off, y + ny * off))
        for (x, y) in pts:
            fill_circle(x, y, 2.2, (250, 206, 110), alpha=alpha)


# ---------------------------------------------------------------------------
# Scene part 3: the golden koi, caption, main
# ---------------------------------------------------------------------------

KOI_ARC = ((300, 792), (430, 400), (775, 345))  # tail -> head (near moon)


def koi_width(t):
    """Body half-width along the arc: slim tail, fat belly, tapered head."""
    return 12 + 52 * (math.sin(math.pi * (0.08 + 0.84 * t)) ** 1.0)


def draw_koi():
    arc = bezier(*KOI_ARC)
    n = len(arc) - 1
    # body outline: left/right offset points along the curve
    left, right = [], []
    for i, (x, y) in enumerate(arc):
        t = i / n
        j = min(i + 1, n)
        dx = arc[j][0] - arc[max(i - 1, 0)][0]
        dy = arc[j][1] - arc[max(i - 1, 0)][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = koi_width(t)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    body = left + right[::-1]
    # dark rim, then gold body
    fill_polygon([(x, y) for x, y in body], (122, 62, 6))
    # inner gold body, slightly inset from the rim
    left_i, right_i = [], []
    for i, (x, y) in enumerate(arc):
        t = i / n
        j = min(i + 1, n)
        dx = arc[j][0] - arc[max(i - 1, 0)][0]
        dy = arc[j][1] - arc[max(i - 1, 0)][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = max(2.0, koi_width(t) - 3.5)
        left_i.append((x + nx * w, y + ny * w))
        right_i.append((x - nx * w, y - ny * w))
    fill_polygon(left_i + right_i[::-1], (238, 155, 11))
    # warm back stripe along the top edge (proper outline: outer + inner)
    outer, inner_s = [], []
    for i, (x, y) in enumerate(arc):
        t = i / n
        if t < 0.06 or t > 0.97:
            continue
        j = min(i + 1, n)
        dx = arc[j][0] - arc[max(i - 1, 0)][0]
        dy = arc[j][1] - arc[max(i - 1, 0)][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = koi_width(t) - 3.5
        outer.append((x + nx * w, y + ny * w))
        inner_s.append((x + nx * (w - 13), y + ny * (w - 13)))
    fill_polygon(outer + inner_s[::-1], (201, 106, 6))
    # creamy belly on the lower side (proper outline: outer + inner)
    outer_b, inner_b = [], []
    for i, (x, y) in enumerate(arc):
        t = i / n
        if t < 0.10 or t > 0.95:
            continue
        j = min(i + 1, n)
        dx = arc[j][0] - arc[max(i - 1, 0)][0]
        dy = arc[j][1] - arc[max(i - 1, 0)][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = koi_width(t) - 3.5
        outer_b.append((x - nx * (w - 2), y - ny * (w - 2)))
        inner_b.append((x - nx * (w - 22), y - ny * (w - 22)))
    fill_polygon(outer_b + inner_b[::-1], (255, 233, 174))
    # white patches + black spots on the flank
    for (tt, off, rw, rh) in [(0.34, 8, 26, 15), (0.55, -4, 30, 17),
                              (0.72, 10, 22, 13)]:
        x, y = arc[int(tt * n)]
        fill_ellipse(x, y + off, rw, rh, (255, 246, 220))
    for (tt, off, rr) in [(0.28, -14, 7), (0.47, 12, 9), (0.63, -16, 6),
                          (0.80, 4, 8)]:
        x, y = arc[int(tt * n)]
        fill_ellipse(x, y + off, rr, rr * 0.8, (42, 26, 8))
    # red-orange patch near the head
    hx, hy = arc[int(0.88 * n)]
    fill_ellipse(hx - 6, hy - 8, 20, 12, (217, 79, 30))
    # dorsal fin: three smooth swept fins along the top edge, mid-body
    for tt in (0.34, 0.50, 0.66):
        x, y = arc[int(tt * n)]
        j = min(int(tt * n) + 1, n)
        dx = arc[j][0] - arc[max(int(tt * n) - 1, 0)][0]
        dy = arc[j][1] - arc[max(int(tt * n) - 1, 0)][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = koi_width(tt)
        # dorsal fin sits on the sky-facing (upper-left) side: -normal
        bx, by = x - nx * w, y - ny * w
        tx, ty = x - nx * (w + 34), y - ny * (w + 34)
        ux, uy = dx / L, dy / L
        fill_polygon([(bx - ux * 20 - nx * 2, by - uy * 20 - ny * 2),
                      (tx, ty),
                      (bx + ux * 20 - nx * 2, by + uy * 20 - ny * 2)],
                     (226, 110, 16), alpha=0.92)
    # pectoral fin near the head, lower side
    px, py = arc[int(0.86 * n)]
    fill_polygon([(px - 8, py + 18), (px + 26, py + 52), (px + 34, py + 20)],
                 (226, 110, 16), alpha=0.92)
    fill_polygon([(px - 2, py + 20), (px + 24, py + 46), (px + 28, py + 22)],
                 (255, 233, 174), alpha=0.85)
    # flowing tail fin at the cup end: two curved lobes sweeping back
    # along the arc's tangent (down-left), forked like a swallowtail
    tx0, ty0 = arc[0]
    tx1, ty1 = arc[3]
    ux, uy = tx0 - tx1, ty0 - ty1
    UL = math.hypot(ux, uy) or 1.0
    ux, uy = ux / UL, uy / UL          # unit tangent pointing back to cup
    nx, ny = -uy, ux                   # unit normal
    # upper lobe (long, sweeping up-left)
    fill_polygon([(tx0 + nx * 8, ty0 + ny * 8),
                  (tx0 + ux * 52 + nx * 36, ty0 + uy * 52 + ny * 36),
                  (tx0 + ux * 70 + nx * 20, ty0 + uy * 70 + ny * 20),
                  (tx0 + ux * 56 + nx * 2, ty0 + uy * 56 + ny * 2),
                  (tx0 - nx * 6, ty0 - ny * 6)],
                 (238, 155, 11))
    fill_polygon([(tx0 + nx * 8, ty0 + ny * 8),
                  (tx0 + ux * 42 + nx * 28, ty0 + uy * 42 + ny * 28),
                  (tx0 + ux * 58 + nx * 16, ty0 + uy * 58 + ny * 16),
                  (tx0 + ux * 46 + nx * 2, ty0 + uy * 46 + ny * 2)],
                 (255, 233, 174), alpha=0.75)
    # lower lobe (shorter, sweeping down-left)
    fill_polygon([(tx0 - nx * 8, ty0 - ny * 8),
                  (tx0 + ux * 44 - nx * 30, ty0 + uy * 44 - ny * 30),
                  (tx0 + ux * 60 - nx * 16, ty0 + uy * 60 - ny * 16),
                  (tx0 + ux * 48 - nx * 2, ty0 + uy * 48 - ny * 2),
                  (tx0 + nx * 6, ty0 + ny * 6)],
                 (226, 110, 16))
    # head + eye + whiskers
    ex, ey = arc[int(0.94 * n)]
    fill_circle(ex + 2, ey - 4, 7.5, (30, 18, 8))
    fill_circle(ex + 0, ey - 6.5, 2.4, (255, 255, 255))
    # barbels from the snout toward the moon
    snx, sny = arc[n]
    for (dx, dy) in [(26, -34), (34, -18)]:
        for k in range(12):
            t = k / 11.0
            fill_circle(snx + dx * t, sny + dy * t - 4 * t * t, 1.8,
                        (250, 220, 150))
    return arc


# 5x7 bitmap font (only glyphs the caption needs + full A-Z for safety)
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


def draw_text_block(lines, x, y, scale, color, outline):
    """Draw lines of bitmap text with a dark outline for readability."""
    line_h = 7 * scale + 20
    # soft dark panel behind each line so it reads over the stars
    # (per-line width, so the panel never touches the moon)
    for li, line in enumerate(lines):
        cy = y + li * line_h
        fill_polygon([(x - 18, cy - 18), (x + len(line) * 6 * scale + 6, cy - 18),
                      (x + len(line) * 6 * scale + 6, cy + line_h + 2),
                      (x - 18, cy + line_h + 2)],
                     (10, 14, 40), alpha=0.30)
    for li, line in enumerate(lines):
        cy = y + li * line_h
        # outline pass (8 neighbours)
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2),
                       (-2, -2), (2, -2), (-2, 2), (2, 2)]:
            _draw_line_text(line, x + ox, cy + oy, scale, outline)
        _draw_line_text(line, x, cy, scale, color)


def _draw_line_text(line, x, y, scale, color):
    cx = x
    for ch in line:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    fill_polygon(
                        [(cx + gx * scale, y + gy * scale),
                         (cx + (gx + 1) * scale, y + gy * scale),
                         (cx + (gx + 1) * scale, y + (gy + 1) * scale),
                         (cx + gx * scale, y + (gy + 1) * scale)],
                        color)
        cx += 6 * scale


def main():
    draw_sky()
    draw_moon()
    draw_tabletop()
    draw_teacup()
    draw_steam()
    draw_splash()
    arc = draw_koi()
    draw_motion_streaks(arc)
    draw_text_block(["TOO BIG FOR THE CUP.", "SHE JUMPED ANYWAY."],
                    48, 56, 6, (255, 243, 214), (16, 10, 34))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "entry.png")
    write_png(path)
    print("wrote", path)


if __name__ == "__main__":
    main()
