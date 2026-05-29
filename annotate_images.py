from PIL import Image, ImageDraw, ImageFont
import math
import os

IMAGES_DIR = r"C:\Users\olive\Documents\Fjeldmann\2605_Kontekst_Guides\images"

TEAL = (2, 89, 81)
GOLD = (190, 133, 19)
WHITE = (255, 255, 255)


def edge_point(cx, cy, bw, bh, tx, ty):
    """Return the point on the label box edge in the direction of (tx, ty)."""
    dx = tx - cx
    dy = ty - cy
    hw = bw / 2.0
    hh = bh / 2.0
    if dx == 0 and dy == 0:
        return (int(cx), int(cy + hh))
    ts = []
    if dx != 0:
        ts.append(hw / abs(dx))
    if dy != 0:
        ts.append(hh / abs(dy))
    t = min(ts)
    return (int(cx + t * dx), int(cy + t * dy))


def draw_arrow(draw, x1, y1, x2, y2, color, width=3, head=14):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(angle - math.pi / 6),
          y2 - head * math.sin(angle - math.pi / 6))
    p2 = (x2 - head * math.cos(angle + math.pi / 6),
          y2 - head * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), p1, p2], fill=color)


def annotate_element(draw, font, text, lcx, lcy, tx, ty, color):
    """Draw label centered at (lcx,lcy) with an arrow tip at (tx,ty)."""
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad = 10
    bw = tw + pad * 2
    bh = th + pad * 2

    lx1 = lcx - bw // 2
    ly1 = lcy - bh // 2

    draw.rounded_rectangle([lx1, ly1, lx1 + bw, ly1 + bh], radius=6, fill=color)
    draw.text((lx1 + pad, ly1 + pad - bbox[1]), text, fill=WHITE, font=font)

    ex, ey = edge_point(lcx, lcy, bw, bh, tx, ty)
    draw_arrow(draw, ex, ey, tx, ty, color)


def process(filename, annotations, out_suffix="_ann"):
    src = os.path.join(IMAGES_DIR, filename)
    base, ext = os.path.splitext(filename)
    dst = os.path.join(IMAGES_DIR, base + out_suffix + ext)

    img = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    except Exception:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
        except Exception:
            font = ImageFont.load_default()

    for ann in annotations:
        annotate_element(draw, font,
                         ann["text"],
                         ann["lcx"], ann["lcy"],
                         ann["tx"], ann["ty"],
                         ann.get("color", TEAL))

    img.save(dst, "PNG")
    print(f"  Saved: {os.path.basename(dst)}")


# ---------------------------------------------------------------------------
# Per-image annotations  (lcx, lcy = label centre;  tx, ty = arrow tip)
# ---------------------------------------------------------------------------

# Trin 1 – chat lobby  (933×583)
process("chat lobby.png", [
    {"text": "Tryk 'Inviter deltager'", "lcx": 720, "lcy": 110, "tx": 590, "ty": 222, "color": GOLD},
    {"text": "QR uden invitation",      "lcx": 168, "lcy": 455, "tx": 168, "ty": 360, "color": GOLD},
])

# Trin 2 – invite filled name  (891×555)
process("chat invite filled name .png", [
    {"text": "Navn",       "lcx": 450, "lcy": 190, "tx": 490, "ty": 268, "color": GOLD},
    {"text": "Vælg sprog", "lcx": 665, "lcy": 175, "tx": 700, "ty": 268, "color": GOLD},
    {"text": "Bekræft",    "lcx": 830, "lcy": 130, "tx": 800, "ty": 268, "color": GOLD},
])

# Trin 3 – QR after invitation  (967×681) – modal overlay
process("chat qr after invitation.png", [
    {"text": "Scan QR-koden",       "lcx": 780, "lcy": 230, "tx": 563, "ty": 340, "color": GOLD},
    {"text": "Klik for at kopiere", "lcx": 780, "lcy": 510, "tx": 735, "ty": 551, "color": GOLD},
])

# Trin 4 – join page  (831×686)
process("join page.png", [
    {"text": "Navn og sprog er udfyldt", "lcx": 665, "lcy": 415, "tx": 510, "ty": 397, "color": GOLD},
    {"text": "Borgeren trykker 'Join'",  "lcx": 665, "lcy": 540, "tx": 510, "ty": 534, "color": GOLD},
])

# Trin 5 – lobby after join  (925×552)
process("chat lobby after join.png", [
    {"text": "Afventer godkendelse", "lcx": 420, "lcy": 115, "tx": 360, "ty": 202, "color": GOLD},
    {"text": "Acceptér",             "lcx": 690, "lcy": 115, "tx": 765, "ty": 202, "color": GOLD},
    {"text": "Afvis",                "lcx": 830, "lcy": 265, "tx": 800, "ty": 235, "color": (180, 50, 50)},
])

# Trin 6 – lobby after accept  (929×599)
process("chat lobby after accept.png", [
    {"text": "Godkendt",             "lcx": 430, "lcy": 112, "tx": 370, "ty": 205, "color": GOLD},
    {"text": "Tryk 'Start samtale'", "lcx": 700, "lcy": 515, "tx": 449, "ty": 465, "color": GOLD},
])

# Trin 7 – session (idle)  (1247×822)
process("chat session .png", [
    {"text": "Tryk for at optage",         "lcx": 391, "lcy": 668, "tx": 391, "ty": 748, "color": GOLD},
    {"text": "Skriv direkte",              "lcx": 810, "lcy": 668, "tx": 810, "ty": 748, "color": GOLD},
])

# Trin 8 – session recording  (1227×821)
process("chat session recording.png", [
    {"text": "Optager - tryk for at stoppe", "lcx": 760, "lcy": 665, "tx": 391, "ty": 748, "color": (180, 50, 50)},
])

# Trin 9 – session send  (1258×818)
process("chat session send.png", [
    {"text": "Transskriberet tekst", "lcx": 700, "lcy": 662, "tx": 790, "ty": 745, "color": GOLD},
    {"text": "Send",                 "lcx": 1070,"lcy": 662, "tx": 1190,"ty": 745, "color": GOLD},
])

# Trin 10 – message received  (1249×826)
process("chat session message recieved.png", [
    {"text": "Auto-afspil beskeder",            "lcx": 480, "lcy": 430, "tx": 52,  "ty": 480, "color": GOLD},
    {"text": "Send stemmeoptagelser automatisk", "lcx": 600, "lcy": 555, "tx": 52,  "ty": 527, "color": GOLD},
    {"text": "Afspil denne besked",              "lcx": 900, "lcy": 118, "tx": 672, "ty": 158, "color": GOLD},
])

print("\nDone!")
