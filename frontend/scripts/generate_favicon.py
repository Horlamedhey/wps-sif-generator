from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/HelveticaNeue.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_oman_emblem(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    size: int,
    color: tuple[int, int, int, int],
) -> None:
    """
    A simple stylized emblem (not an exact official trace): crossed swords + central dagger.
    Designed to remain legible after downscaling to favicon sizes.
    """

    sword_w = max(6, size // 36)

    r = size // 2
    x1, y1 = cx - r, cy - r
    x2, y2 = cx + r, cy + r

    # Crossed swords (two arcs)
    draw.arc((x1, y1 + size // 6, x2, y2 + size // 6), start=210, end=330, fill=color, width=sword_w)
    draw.arc((x1, y1 + size // 6, x2, y2 + size // 6), start=30, end=150, fill=color, width=sword_w)

    # Hilts
    hilt = size // 8
    draw.line((cx - r + hilt, cy + r // 3, cx - r + hilt * 2, cy + r // 3 - hilt // 2), fill=color, width=sword_w)
    draw.line((cx + r - hilt, cy + r // 3, cx + r - hilt * 2, cy + r // 3 - hilt // 2), fill=color, width=sword_w)

    # Central dagger (blade + handle)
    blade_top = cy - size // 4
    blade_bottom = cy + size // 3
    blade_half = size // 10
    draw.polygon(
        [
            (cx, blade_bottom),
            (cx - blade_half, blade_top + size // 10),
            (cx, blade_top),
            (cx + blade_half, blade_top + size // 10),
        ],
        fill=color,
    )

    handle_h = size // 6
    draw.rounded_rectangle(
        (cx - blade_half, blade_top - handle_h, cx + blade_half, blade_top - handle_h // 3),
        radius=size // 30,
        fill=color,
    )

    # Belt-like bar behind dagger
    bar_h = max(10, size // 14)
    draw.rounded_rectangle(
        (cx - r + size // 8, cy + size // 10, cx + r - size // 8, cy + size // 10 + bar_h),
        radius=bar_h // 2,
        fill=color,
    )


def generate(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Oman flag colors (approximate).
    oman_red = (200, 16, 46, 255)  # ~#C8102E
    oman_green = (0, 122, 61, 255)  # ~#007A3D
    oman_white = (255, 255, 255, 255)

    # Foreground palette.
    text_black = (10, 10, 12, 255)
    # Use the emblem in its original black (as a subtle watermark on the paper).
    emblem_black = (10, 10, 12, 255)
    paper = (255, 255, 255, 222)  # slightly transparent, still readable on white
    fold = (235, 242, 255, 228)
    shadow = (0, 0, 0, 44)
    paper_outline = (20, 35, 60, 34)

    size = 512

    # Background: Oman flag layout (red hoist band + white/green horizontals).
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    red_w = int(size * 0.30)
    bd.rectangle((0, 0, red_w, size), fill=oman_red)
    bd.rectangle((red_w, 0, size, size // 2), fill=oman_white)
    bd.rectangle((red_w, size // 2, size, size), fill=oman_green)

    # Rounded square mask (favicon style).
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, size, size), radius=96, fill=255)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas = Image.composite(bg, canvas, mask)

    # Subtle highlight for depth.
    highlight = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    hd.ellipse((-90, -140, 380, 320), fill=(255, 255, 255, 36))
    canvas = Image.alpha_composite(canvas, highlight)

    # Foreground "document" sheet.
    sheet = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheet)

    sheet_box = (122, 92, 390, 424)
    sd.rounded_rectangle(
        (sheet_box[0] + 10, sheet_box[1] + 14, sheet_box[2] + 10, sheet_box[3] + 14),
        radius=44,
        fill=shadow,
    )
    sd.rounded_rectangle(sheet_box, radius=44, fill=paper)
    sd.rounded_rectangle(sheet_box, radius=44, outline=paper_outline, width=3)

    # Folded corner.
    fold_w = 92
    x2, y1 = sheet_box[2], sheet_box[1]
    fold_poly = [(x2 - fold_w, y1), (x2, y1), (x2, y1 + fold_w)]
    sd.polygon(fold_poly, fill=fold)
    sd.line([(x2 - fold_w, y1), (x2, y1 + fold_w)], fill=(190, 210, 245, 255), width=6)

    # Text: WPS top, SIF bottom.
    font_wps = _load_font(62)
    font_sif = _load_font(92)

    def center_text(text: str, font: ImageFont.ImageFont, y: int) -> None:
        bbox = sd.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        tx = (sheet_box[0] + sheet_box[2] - tw) // 2
        sd.text((tx, y), text, font=font, fill=text_black)

    # Positions tuned so there's room for the emblem between the labels.
    wps_y = 112
    sif_y = 326

    wps_bbox = sd.textbbox((0, 0), "WPS", font=font_wps)
    wps_h = max(1, wps_bbox[3] - wps_bbox[1])
    gap_top = wps_y + wps_h
    gap = max(1, sif_y - gap_top)

    # Oman emblem ON the sheet, centered between WPS and SIF.
    emblem_path = ASSETS_DIR / "oman-emblem.png"
    if emblem_path.exists():
        try:
            em = Image.open(emblem_path).convert("RGBA")
            a = em.getchannel("A")
            bbox = a.getbbox()
            if bbox:
                em = em.crop(bbox)

            # Size based on available gap; allow some breathing room.
            emblem_sz = max(72, min(190, int(gap * 0.88)))
            em = em.resize((emblem_sz, emblem_sz), resample=Image.Resampling.LANCZOS)

            a = em.getchannel("A").point(lambda p: int(p * 0.26))
            em_col = Image.new("RGBA", em.size, emblem_black)
            em_col.putalpha(a)

            ex = (sheet_box[0] + sheet_box[2] - emblem_sz) // 2
            ey_center = (gap_top + sif_y) // 2
            ey = ey_center - (emblem_sz // 2)
            sheet.alpha_composite(em_col, (ex, ey))
        except Exception:
            # Fallback to a simple drawn emblem if the asset can't be loaded.
            _draw_oman_emblem(
                sd,
                cx=(sheet_box[0] + sheet_box[2]) // 2,
                cy=(gap_top + sif_y) // 2,
                size=250,
                color=(33, 74, 145, 46),
            )
    else:
        _draw_oman_emblem(
            sd,
            cx=(sheet_box[0] + sheet_box[2]) // 2,
            cy=(gap_top + sif_y) // 2,
            size=250,
            color=(33, 74, 145, 46),
        )

    # Draw text after emblem so it stays crisp.
    center_text("WPS", font_wps, y=wps_y)
    center_text("SIF", font_sif, y=sif_y)

    canvas = Image.alpha_composite(canvas, sheet)

    # Save base icons.
    canvas.save(out_dir / "android-chrome-512x512.png")

    # Resize variants.
    for sz, name in [
        (192, "android-chrome-192x192.png"),
        (180, "apple-touch-icon.png"),
        (32, "favicon-32x32.png"),
        (16, "favicon-16x16.png"),
    ]:
        canvas.resize((sz, sz), resample=Image.Resampling.LANCZOS).save(out_dir / name)

    # ICO (16/32/48).
    canvas.resize((48, 48), resample=Image.Resampling.LANCZOS).save(
        out_dir / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )


if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "static")
