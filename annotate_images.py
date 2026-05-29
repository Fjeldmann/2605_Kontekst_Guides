from PIL import Image, ImageDraw, ImageFont
import math
import os

IMAGES_DIR = r"C:\Users\olive\Documents\Fjeldmann\2601_Kontekst_Kommunesalg\images"

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

# Trin 1 – chat lobby
process("chat lobby.png", [
    {"text": "Tryk 'Inviter deltager'", "lcx": 680, "lcy": 155, "tx": 612, "ty": 225, "color": GOLD},
    {"text": "QR-kode til borgeren",   "lcx": 190, "lcy": 410, "tx": 190, "ty": 295, "color": GOLD},
])

# Trin 2 – invite filled name
process("chat invite filled name .png", [
    {"text": "Navn",          "lcx": 450, "lcy": 235, "tx": 585, "ty": 308, "color": GOLD},
    {"text": "Vælg sprog",    "lcx": 920, "lcy": 235, "tx": 798, "ty": 308, "color": GOLD},
    {"text": "Bekræft",     "lcx": 1060,"lcy": 308, "tx": 895, "ty": 308, "color": GOLD},
])

# Trin 3 – QR after invitation
process("chat qr after invitation.png", [
    {"text": "Scan QR-koden",    "lcx": 850, "lcy": 280, "tx": 698, "ty": 338, "color": GOLD},
    {"text": "Eller kopiér link","lcx": 850, "lcy": 500, "tx": 726, "ty": 500, "color": GOLD},
])

# Trin 4 – join page
process("join page.png", [
    {"text": "Navn og sprog er udfyldt", "lcx": 200, "lcy": 423, "tx": 362, "ty": 423, "color": GOLD},
    {"text": "Borgeren trykker 'Join'",  "lcx": 200, "lcy": 560, "tx": 357, "ty": 560, "color": GOLD},
])

# Trin 5 – lobby after join
process("chat lobby after join.png", [
    {"text": "Afventer godkendelse", "lcx": 580, "lcy": 155, "tx": 570, "ty": 205, "color": GOLD},
    {"text": "Acceptér",            "lcx": 860, "lcy": 155, "tx": 806, "ty": 232, "color": GOLD},
    {"text": "Afvis",               "lcx": 860, "lcy": 265, "tx": 840, "ty": 232, "color": (180, 50, 50)},
])

# Trin 6 – lobby after accept
process("chat lobby after accept.png", [
    {"text": "Godkendt",            "lcx": 580, "lcy": 150, "tx": 375, "ty": 208, "color": GOLD},
    {"text": "Tryk 'Start samtale'",  "lcx": 680, "lcy": 450, "tx": 472, "ty": 487, "color": GOLD},
])

# Trin 7 – session (idle)
process("chat session .png", [
    {"text": "Tryk for at optage",    "lcx": 400, "lcy": 700, "tx": 400, "ty": 762, "color": GOLD},
    {"text": "Eller skriv direkte",   "lcx": 850, "lcy": 700, "tx": 800, "ty": 762, "color": GOLD},
    {"text": "Auto-afspil beskeder",  "lcx": 420, "lcy": 470, "tx": 175, "ty": 470, "color": GOLD},
])

# Trin 8 – session recording
process("chat session recording.png", [
    {"text": "Optager – tryk for at stoppe", "lcx": 700, "lcy": 700, "tx": 395, "ty": 762, "color": (180, 50, 50)},
])

# Trin 9 – session send
process("chat session send.png", [
    {"text": "Transskriberet tekst", "lcx": 700, "lcy": 700, "tx": 640, "ty": 762, "color": GOLD},
    {"text": "Send",                "lcx": 1100,"lcy": 700, "tx": 1185,"ty": 762, "color": GOLD},
])

# Trin 10 – message received
process("chat session message recieved.png", [
    {"text": "Auto-afspil (til/fra)", "lcx": 420, "lcy": 462, "tx": 200, "ty": 462, "color": GOLD},
    {"text": "Afspil denne besked",   "lcx": 820, "lcy": 158, "tx": 670, "ty": 158, "color": GOLD},
])

print("\nDone!")
