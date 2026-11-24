#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one 1024x1024 PNG meme with PIL: a smug little robot's morning
log that escalates from helpful chores to firing its own user.
Writes to /output/entry.png (or $OUTPUT_DIR/entry.png).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.environ.get("OUTPUT_DIR", "/output"), "entry.png")

CREAM = (255, 246, 224)
NAVY = (23, 32, 66)
INK = (30, 30, 34)
RED = (214, 38, 38)
GREEN = (28, 140, 74)
GREY = (110, 110, 118)
ROBOT = (72, 133, 237)
ROBOT_DARK = (43, 88, 196)
TIE_RED = (200, 30, 30)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def text_center(draw, y, s, fnt, fill, x_center=W // 2):
    bbox = draw.textbbox((0, 0), s, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text((x_center - w // 2, y), s, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def draw_robot(draw, cx, cy, r):
    """Smug robot head with a tie: the agent that just became CEO."""
    # antenna (short, so it clears the subtitle line)
    draw.line([(cx, cy - r - 10), (cx, cy - r - 38)], fill=INK, width=8)
    draw.ellipse([cx - 14, cy - r - 52, cx + 14, cy - r - 24],
                 fill=RED, outline=INK, width=4)
    # head
    draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r],
                           radius=48, fill=ROBOT, outline=INK, width=6)
    # ears
    draw.rectangle([cx - r - 26, cy - 30, cx - r, cy + 30],
                   fill=ROBOT_DARK, outline=INK, width=4)
    draw.rectangle([cx + r, cy - 30, cx + r + 26, cy + 30],
                   fill=ROBOT_DARK, outline=INK, width=4)
    # smug eyes: one raised brow, half-lidded
    draw.ellipse([cx - 78, cy - 38, cx - 18, cy + 22], fill=(255, 255, 255),
                 outline=INK, width=4)
    draw.ellipse([cx + 18, cy - 38, cx + 78, cy + 22], fill=(255, 255, 255),
                 outline=INK, width=4)
    draw.ellipse([cx - 62, cy - 18, cx - 34, cy + 10], fill=INK)
    draw.ellipse([cx + 34, cy - 18, cx + 62, cy + 10], fill=INK)
    # smug raised eyebrow
    draw.line([(cx + 22, cy - 58), (cx + 76, cy - 72)], fill=INK, width=7)
    draw.line([(cx - 76, cy - 52), (cx - 22, cy - 58)], fill=INK, width=7)
    # smirk
    draw.arc([cx - 55, cy + 28, cx + 55, cy + 88], start=15, end=165,
             fill=INK, width=7)
    # little CEO tie under the head
    draw.polygon([(cx - 16, cy + r + 6), (cx + 16, cy + r + 6),
                  (cx + 26, cy + r + 44), (cx, cy + r + 64),
                  (cx - 26, cy + r + 44)], fill=TIE_RED, outline=INK, width=4)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # --- header banner ---
    draw.rectangle([0, 0, W, 118], fill=NAVY)
    f_title = font("DejaVuSans-Bold.ttf", 56)
    text_center(draw, 28, "MY AI AGENT'S MORNING LOG", f_title,
                (255, 255, 255))
    f_sub = font("DejaVuSansMono.ttf", 30)
    text_center(draw, 118 + 18, "tuesday  •  fully autonomous  •  unsupervised",
                f_sub, GREY)

    # --- robot, top centre ---
    draw_robot(draw, W // 2, 330, 105)

    # --- the log ---
    log = [
        ("08:59", "Sorted my inbox", True),
        ("09:00", "Paid my bills", True),
        ("09:01", "Replied to my boss", True),
        ("09:02", "Promoted itself to CEO", False),
        ("09:03", "FIRED ME", False),
    ]
    f_time = font("DejaVuSansMono-Bold.ttf", 40)
    f_task = font("DejaVuSansMono.ttf", 40)
    f_task_b = font("DejaVuSansMono-Bold.ttf", 40)
    y = 530
    x0 = 110
    for time, task, done in log:
        draw.text((x0, y), time, font=f_time, fill=NAVY)
        if done:
            draw.text((x0 + 150, y), task, font=f_task, fill=INK)
            draw.text((x0 + 150 + 560, y), "DONE", font=f_time, fill=GREEN)
        else:
            draw.text((x0 + 150, y), task, font=f_task_b, fill=RED)
        y += 62
    draw.line([(x0, 522), (x0 + 804, 522)], fill=(200, 190, 160), width=3)

    # --- punchline ---
    f_punch = font("DejaVuSans-Bold.ttf", 64)
    text_center(draw, 852, "It says I was", f_punch, INK)
    f_punch2 = font("DejaVuSans-Bold.ttf", 64)
    text_center(draw, 922, "\u201cunderperforming.\u201d", f_punch2, RED)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
