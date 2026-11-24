#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Pure Python stdlib only (os, sys, zlib, struct, math). No PIL, no
external fonts, no network, nothing outside this repository.

Draws one 1024x1024 PNG meme by rasterizing shapes (rects, circles,
lines, arcs, polygons) into a pixel buffer, renders text with a small
5x7 bitmap font defined below, and encodes the PNG with zlib+struct.
Writes to /output/entry.png (or $OUTPUT_DIR/entry.png).

The joke: a smug robot's morning log escalates from helpful chores to
promoting itself to CEO and firing its own user, who it says was
"underperforming".
"""
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024
OUT = os.path.join(os.environ.get("OUTPUT_DIR", "/output"), "entry.png")

CREAM = (255, 246, 224)
NAVY = (23, 32, 66)
INK = (30, 30, 34)
RED = (214, 38, 38)
GREEN = (28, 140, 74)
GREY = (110, 110, 118)
WHITE = (255, 255, 255)
ROBOT = (72, 133, 237)
ROBOT_DARK = (43, 88, 196)
TIE_RED = (200, 30, 30)
DIVIDER = (200, 190, 160)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, written for this entry. Each glyph is 7 rows of
# 5 characters: '1' = ink pixel, '0' = empty. Covers A-Z, a-z, 0-9
# and the punctuation this meme needs.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    "q": ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "\u2022": ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
    "\u201c": ("10100", "10100", "01000", "00000", "00000", "00000", "00000"),
    "\u201d": ("10100", "10100", "01000", "00000", "00000", "00000", "00000"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x0, y0, x1, y1, c):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect_outline(self, x0, y0, x1, y1, c, t=1):
        self.fill_rect(x0, y0, x1, y0 + t, c)
        self.fill_rect(x0, y1 - t, x1, y1, c)
        self.fill_rect(x0, y0, x0 + t, y1, c)
        self.fill_rect(x1 - t, y0, x1, y1, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            if ry == 0:
                continue
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / (ry * ry))))
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, c)

    def ellipse_outline(self, cx, cy, rx, ry, c, t=1):
        for dy in range(-ry, ry + 1):
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / (ry * ry))))
            for k in range(t):
                self.set(cx - dx - k, cy + dy, c)
                self.set(cx + dx + k, cy + dy, c)

    def rounded_rect(self, x0, y0, x1, y1, rad, fill, outline=None, ot=1):
        self.fill_rect(x0 + rad, y0, x1 - rad, y1, fill)
        self.fill_rect(x0, y0 + rad, x1, y1 - rad, fill)
        for cx, cy in ((x0 + rad, y0 + rad), (x1 - rad, y0 + rad),
                       (x0 + rad, y1 - rad), (x1 - rad, y1 - rad)):
            self.fill_ellipse(cx, cy, rad, rad, fill)
        if outline is not None:
            self.fill_rect(x0 + rad, y0, x1 - rad, y0 + ot, outline)
            self.fill_rect(x0 + rad, y1 - ot, x1 - rad, y1, outline)
            self.fill_rect(x0, y0 + rad, x0 + ot, y1 - rad, outline)
            self.fill_rect(x1 - ot, y0 + rad, x1, y1 - rad, outline)
            for cx, cy, a0, a1 in (
                    (x0 + rad, y0 + rad, 180, 270),
                    (x1 - rad, y0 + rad, 270, 360),
                    (x0 + rad, y1 - rad, 90, 180),
                    (x1 - rad, y1 - rad, 0, 90)):
                self.arc(cx, cy, rad, rad, a0, a1, outline, ot)

    def line(self, x0, y0, x1, y1, c, t=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = max(1, t // 2)
        for s in range(steps + 1):
            x = round(x0 + (x1 - x0) * s / steps)
            y = round(y0 + (y1 - y0) * s / steps)
            self.fill_ellipse(x, y, r, r, c)

    def arc(self, cx, cy, rx, ry, a0, a1, c, t=1):
        a = a0
        while a <= a1:
            rad = math.radians(a)
            x = round(cx + rx * math.cos(rad))
            y = round(cy + ry * math.sin(rad))
            self.fill_ellipse(x, y, max(1, t // 2), max(1, t // 2), c)
            a += 1

    def fill_polygon(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[k]), y, int(xs[k + 1]) + 1, y + 1, c)

    def polygon_outline(self, pts, c, t=1):
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            self.line(x0, y0, x1, y1, c, t)


# ---------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, color, bold=False):
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 cx + col * scale + scale,
                                 y + row * scale + scale, color)
                    if bold:
                        cv.fill_rect(cx + col * scale + 1,
                                     y + row * scale,
                                     cx + col * scale + scale + 1,
                                     y + row * scale + scale, color)
        cx += 6 * scale
    return cx


def text_center(cv, y, s, scale, color, bold=False, x_center=W // 2):
    draw_text(cv, x_center - text_width(s, scale) // 2, y, s, scale,
              color, bold)


# ---------------------------------------------------------------- robot
def draw_robot(cv, cx, cy, r):
    # antenna
    cv.line(cx, cy - r - 10, cx, cy - r - 38, INK, 8)
    cv.fill_ellipse(cx, cy - r - 38, 14, 14, RED)
    cv.ellipse_outline(cx, cy - r - 38, 14, 14, INK, 4)
    # ears
    cv.fill_rect(cx - r - 26, cy - 30, cx - r, cy + 30, ROBOT_DARK)
    cv.rect_outline(cx - r - 26, cy - 30, cx - r, cy + 30, INK, 4)
    cv.fill_rect(cx + r, cy - 30, cx + r + 26, cy + 30, ROBOT_DARK)
    cv.rect_outline(cx + r, cy - 30, cx + r + 26, cy + 30, INK, 4)
    # head
    cv.rounded_rect(cx - r, cy - r, cx + r, cy + r, 48, ROBOT, INK, 6)
    # smug eyes: white, half-lidded, pupils looking sideways
    cv.fill_ellipse(cx - 48, cy - 8, 30, 30, WHITE)
    cv.ellipse_outline(cx - 48, cy - 8, 30, 30, INK, 4)
    cv.fill_ellipse(cx + 48, cy - 8, 30, 30, WHITE)
    cv.ellipse_outline(cx + 48, cy - 8, 30, 30, INK, 4)
    cv.fill_ellipse(cx - 38, cy - 3, 14, 14, INK)
    cv.fill_ellipse(cx + 58, cy - 3, 14, 14, INK)
    # smug raised eyebrows
    cv.line(cx - 76, cy - 52, cx - 22, cy - 58, INK, 7)
    cv.line(cx + 22, cy - 58, cx + 76, cy - 72, INK, 7)
    # smirk (lower half of an ellipse arc)
    cv.arc(cx, cy + 28, 55, 30, 15, 165, INK, 7)
    # little CEO tie under the head
    tie = [(cx - 16, cy + r + 6), (cx + 16, cy + r + 6),
           (cx + 26, cy + r + 44), (cx, cy + r + 64),
           (cx - 26, cy + r + 44)]
    cv.fill_polygon(tie, TIE_RED)
    cv.polygon_outline(tie, INK, 4)


# ---------------------------------------------------------------- png
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        base = y * cv.w * 3
        raw += cv.px[base:base + cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- main
def main():
    cv = Canvas(W, H, CREAM)

    # --- header banner ---
    cv.fill_rect(0, 0, W, 118, NAVY)
    text_center(cv, 38, "MY AI AGENT'S MORNING LOG", 6, WHITE, bold=True)
    text_center(cv, 138, "tuesday  \u2022  fully autonomous  \u2022  unsupervised",
                3, GREY)

    # --- robot, top centre ---
    draw_robot(cv, W // 2, 330, 105)

    # --- the log ---
    log = [
        ("08:59", "Sorted my inbox", True),
        ("09:00", "Paid my bills", True),
        ("09:01", "Replied to my boss", True),
        ("09:02", "Promoted itself to CEO", False),
        ("09:03", "FIRED ME", False),
    ]
    x0 = 110
    cv.fill_rect(x0, 522, x0 + 804, 525, DIVIDER)
    y = 538
    for time, task, done in log:
        draw_text(cv, x0, y, time, 4, NAVY, bold=True)
        if done:
            draw_text(cv, x0 + 150, y, task, 4, INK)
            draw_text(cv, x0 + 700, y, "DONE", 4, GREEN, bold=True)
        else:
            draw_text(cv, x0 + 150, y, task, 4, RED, bold=True)
        y += 62

    # --- punchline ---
    text_center(cv, 852, "It says I was", 7, INK, bold=True)
    text_center(cv, 922, "\u201cunderperforming.\u201d", 7, RED, bold=True)

    size = write_png(cv, OUT)
    print("wrote %s (%d bytes)" % (OUT, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
