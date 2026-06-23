from PIL import Image, ImageDraw, ImageFont
import math
import os

IMAGES_DIR = r"C:\Users\olive\Documents\Fjeldmann\2605_Kontekst_Guides\images"

TEAL = (2, 89, 81)
GOLD = (190, 133, 19)
WHITE = (255, 255, 255)


def edge_point(cx, cy, bw, bh, tx, ty):
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


def draw_arrow(draw, x1, y1, x2, y2, color, width=4, head=18):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(angle - math.pi / 6),
          y2 - head * math.sin(angle - math.pi / 6))
    p2 = (x2 - head * math.cos(angle + math.pi / 6),
          y2 - head * math.sin(angle + math.pi / 6))
    draw.polygon([(x2, y2), p1, p2], fill=color)


def annotate_element(draw, font, text, lcx, lcy, tx, ty, color, arrow_w=4, arrow_h=18):
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad = max(8, round((bbox[3] - bbox[1]) * 0.45))
    bw = tw + pad * 2
    bh = th + pad * 2
    lx1 = lcx - bw // 2
    ly1 = lcy - bh // 2
    draw.rounded_rectangle([lx1, ly1, lx1 + bw, ly1 + bh], radius=6, fill=color)
    draw.text((lx1 + pad, ly1 + pad - bbox[1]), text, fill=WHITE, font=font)
    ex, ey = edge_point(lcx, lcy, bw, bh, tx, ty)
    draw_arrow(draw, ex, ey, tx, ty, color, width=arrow_w, head=arrow_h)


def process(filename, annotations, out_suffix="_ann"):
    src = os.path.join(IMAGES_DIR, filename)
    base, ext = os.path.splitext(filename)
    dst = os.path.join(IMAGES_DIR, base + out_suffix + ext)
    img = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(img)
    FONT_SIZE = max(16, round(img.width * 0.026))
    arrow_w = max(2, round(img.width * 0.004))
    arrow_h = max(10, round(img.width * 0.016))
    font = None
    for path in [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        try:
            font = ImageFont.truetype(path, FONT_SIZE)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    for ann in annotations:
        annotate_element(draw, font,
                         ann["text"],
                         ann["lcx"], ann["lcy"],
                         ann["tx"], ann["ty"],
                         ann.get("color", TEAL),
                         arrow_w=arrow_w, arrow_h=arrow_h)
    img.save(dst, "PNG")
    print(f"  Saved: {os.path.basename(dst)}")


# Trin 1
process("chat lobby.png", [
    {"text": "Tryk 'Tilføj deltager'", "lcx": 720, "lcy": 110, "tx": 600, "ty": 218, "color": GOLD},
    {"text": "Deltag direkte med QR kode", "lcx": 490, "lcy": 430, "tx": 192, "ty": 395, "color": GOLD},
])

# Trin 2
process("chat invite filled name .png", [
    {"text": "Navn",       "lcx": 450, "lcy": 190, "tx": 459, "ty": 278, "color": GOLD},
    {"text": "Vælg sprog", "lcx": 665, "lcy": 175, "tx": 635, "ty": 278, "color": GOLD},
    {"text": "Tilføj",     "lcx": 830, "lcy": 130, "tx": 790, "ty": 278, "color": GOLD},
])

# Trin 3
process("chat qr after invitation.png", [
    {"text": "Scan QR-koden",       "lcx": 750, "lcy": 220, "tx": 443, "ty": 288, "color": GOLD},
    {"text": "Klik for at kopiere", "lcx": 750, "lcy": 530, "tx": 443, "ty": 540, "color": GOLD},
])

# Trin 4
process("join page.png", [
    {"text": "Navn og sprog er udfyldt", "lcx": 400, "lcy": 250, "tx": 290, "ty": 358, "color": GOLD},
    {"text": "Borgeren trykker Join",    "lcx": 400, "lcy": 565, "tx": 290, "ty": 497, "color": GOLD},
])

# Trin 5
process("chat lobby after join.png", [
    {"text": "Afventer godkendelse", "lcx": 420, "lcy": 110, "tx": 368, "ty": 208, "color": GOLD},
    {"text": "Acceptér",             "lcx": 690, "lcy": 110, "tx": 769, "ty": 208, "color": GOLD},
    {"text": "Afvis",                "lcx": 870, "lcy": 295, "tx": 808, "ty": 208, "color": (180, 50, 50)},
])

# Trin 6
process("chat lobby after accept.png", [
    {"text": "Godkendt",              "lcx": 430, "lcy": 108, "tx": 368, "ty": 208, "color": GOLD},
    {"text": "Tryk Start samtale",    "lcx": 750, "lcy": 450, "tx": 583, "ty": 388, "color": GOLD},
])

# Trin 7
process("chat session .png", [
    {"text": "Tryk for at optage", "lcx": 383, "lcy": 660, "tx": 383, "ty": 766, "color": GOLD},
    {"text": "Skriv direkte",      "lcx": 790, "lcy": 660, "tx": 790, "ty": 766, "color": GOLD},
])

# Trin 8
process("chat session recording.png", [
    {"text": "Optager - tryk stop", "lcx": 760, "lcy": 660, "tx": 383, "ty": 763, "color": (180, 50, 50)},
])

# Trin 9
process("chat session send.png", [
    {"text": "Transskriberet tekst", "lcx": 700,  "lcy": 660, "tx": 790,  "ty": 767, "color": GOLD},
    {"text": "Send",                 "lcx": 1070, "lcy": 660, "tx": 1171, "ty": 767, "color": GOLD},
])

# Trin 10
process("chat session message recieved.png", [
    {"text": "Afspil automatisk",   "lcx": 700, "lcy": 420, "tx": 55,  "ty": 163, "color": GOLD},
    {"text": "Send automatisk",     "lcx": 700, "lcy": 580, "tx": 55,  "ty": 188, "color": GOLD},
    {"text": "Afspil denne besked", "lcx": 900, "lcy": 115, "tx": 621, "ty": 158, "color": GOLD},
])

print("\nDone!")
