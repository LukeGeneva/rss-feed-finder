"""Generates simple RSS-style PNG icons for the extension."""
import struct
import zlib
import os

def png(size, draw_fn):
    def chunk(tag, data):
        buf = tag + data
        return struct.pack(">I", len(data)) + buf + struct.pack(">I", zlib.crc32(buf) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)

    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter: none
        for x in range(size):
            raw.extend(draw_fn(x, y, size))

    signature = b"\x89PNG\r\n\x1a\n"
    return (
        signature
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def draw_icon(x, y, size):
    s = size - 1
    cx, cy = x / s, y / s

    # Rounded rect background: red
    pad = 0.08
    radius = 0.22
    in_bg = (pad <= cx <= 1 - pad) and (pad <= cy <= 1 - cy)

    # Simple approach: full red square background with white RSS arcs
    # Background
    bg = (0xFF, 0x00, 0x00)
    fg = (0xFF, 0xFF, 0xFF)

    nx, ny = cx - pad, cy - pad
    w = 1 - 2 * pad

    # Dot (bottom-left)
    dot_r = 0.10
    dot_cx, dot_cy = pad + 0.14, 1 - pad - 0.14
    dist_dot = ((cx - dot_cx) ** 2 + (cy - dot_cy) ** 2) ** 0.5

    # Arc 1 (small)
    arc1_cx, arc1_cy = pad + 0.08, 1 - pad - 0.08
    arc1_r1, arc1_r2 = 0.22, 0.30
    dist_a1 = ((cx - arc1_cx) ** 2 + (cy - arc1_cy) ** 2) ** 0.5

    # Arc 2 (large)
    arc2_cx, arc2_cy = pad + 0.06, 1 - pad - 0.06
    arc2_r1, arc2_r2 = 0.40, 0.50
    dist_a2 = ((cx - arc2_cx) ** 2 + (cy - arc2_cy) ** 2) ** 0.5

    in_dot = dist_dot < dot_r
    in_arc1 = (arc1_r1 < dist_a1 < arc1_r2) and cx > arc1_cx and cy < arc1_cy
    in_arc2 = (arc2_r1 < dist_a2 < arc2_r2) and cx > arc2_cx and cy < arc2_cy

    # Rounded rect mask
    def in_rounded_rect(px, py, x0, y0, x1, y1, r):
        if px < x0 or px > x1 or py < y0 or py > y1:
            return False
        corners = [(x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)]
        for (ccx, ccy) in corners:
            if px < ccx - r or px > ccx + r or py < ccy - r or py > ccy + r:
                continue
            if ((px - ccx) ** 2 + (py - ccy) ** 2) > r * r:
                return False
        return True

    if not in_rounded_rect(cx, cy, pad, pad, 1 - pad, 1 - pad, radius):
        return (0x00, 0x00, 0x00)  # transparent-ish (black bg)

    if in_dot or in_arc1 or in_arc2:
        return fg
    return bg


def simple_icon(x, y, size):
    """Clean, simpler icon: red rounded rect with white RSS symbol."""
    pad = 1 / size * 1.5
    r = 0.22

    cx, cy = x / (size - 1), y / (size - 1)

    def dist(ax, ay): return ((cx - ax) ** 2 + (cy - ay) ** 2) ** 0.5

    # Rounded rect check
    def in_rrect(px, py, x0, y0, x1, y1, rr):
        if not (x0 <= px <= x1 and y0 <= py <= y1):
            return False
        corners = [(x0 + rr, y0 + rr), (x1 - rr, y0 + rr), (x0 + rr, y1 - rr), (x1 - rr, y1 - rr)]
        for (ccx, ccy) in corners:
            if px < x0 + rr and py < y0 + rr:
                return dist_c(px, py, x0 + rr, y0 + rr) <= rr
            if px > x1 - rr and py < y0 + rr:
                return dist_c(px, py, x1 - rr, y0 + rr) <= rr
            if px < x0 + rr and py > y1 - rr:
                return dist_c(px, py, x0 + rr, y1 - rr) <= rr
            if px > x1 - rr and py > y1 - rr:
                return dist_c(px, py, x1 - rr, y1 - rr) <= rr
        return True

    def dist_c(ax, ay, bx, by): return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5

    if not in_rrect(cx, cy, pad, pad, 1 - pad, 1 - pad, r):
        return (0x00, 0x00, 0x00)

    # RSS origin (bottom-left of icon interior)
    ox, oy = pad + 0.12, 1 - pad - 0.12
    t = 0.5 / size  # stroke thickness (normalized)
    T = max(t, 0.04)

    d = dist_c(cx, cy, ox, oy)

    # Dot
    if d < 0.10:
        return (0xFF, 0xFF, 0xFF)

    # Arc 1
    if 0.20 < d < 0.32 and cx > ox and cy < oy:
        return (0xFF, 0xFF, 0xFF)

    # Arc 2
    if 0.38 < d < 0.50 and cx > ox and cy < oy:
        return (0xFF, 0xFF, 0xFF)

    return (0xFF, 0x00, 0x00)


os.makedirs(os.path.dirname(__file__), exist_ok=True)

for size, name in [(16, "icon16.png"), (48, "icon48.png"), (128, "icon128.png")]:
    path = os.path.join(os.path.dirname(__file__), name)
    with open(path, "wb") as f:
        f.write(png(size, simple_icon))
    print(f"Created {name} ({size}x{size})")
