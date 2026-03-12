"""Run this once to generate the app icons before building."""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ASSETS = pathlib.Path(__file__).parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)


def draw_icon(color: str, size: int = 256) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Background circle with slight gradient feel (two layered ellipses)
    margin = size // 10
    d.ellipse([margin, margin, size - margin, size - margin], fill=color)

    # Inner highlight (top-left lighter arc)
    hi_color = tuple(min(255, c + 40) for c in _hex_to_rgb(color)) + (60,)
    d.ellipse([margin + 4, margin + 4, size // 2, size // 2], fill=hi_color)

    # Letter "R"
    font_size = int(size * 0.52)
    try:
        font = ImageFont.truetype("segoeuib.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    text = "R"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1]
    d.text((tx, ty), text, fill="#FFFFFF", font=font)

    return img


def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def save_ico(img: Image.Image, path: pathlib.Path):
    """Save as multi-resolution .ico and .png."""
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    resized = [img.resize(s, Image.LANCZOS) for s in sizes]
    resized[0].save(str(path), format="ICO", sizes=sizes,
                    append_images=resized[1:])
    # Also save PNG for pystray (works better than ico on some systems)
    png_path = path.with_suffix(".png")
    img.resize((64, 64), Image.LANCZOS).save(str(png_path), format="PNG")
    print(f"Saved {path} + {png_path}")


if __name__ == "__main__":
    normal = draw_icon("#7C6AF7")
    save_ico(normal, ASSETS / "icon.ico")

    working = draw_icon("#555577")
    save_ico(working, ASSETS / "icon_gray.ico")

    print("Icons generated in assets/")
