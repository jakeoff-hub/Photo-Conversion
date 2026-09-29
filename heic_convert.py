#!/usr/bin/env python3
"""Convert HEIC/HEIF photos (or any common image) to JPG/PNG/WebP, or combine them into a PDF.

Examples:
    # One PDF with every photo on its own page
    python heic_convert.py photos/*.heic -o photos.pdf

    # Individual JPGs you can drop into any PDF editor
    python heic_convert.py IMG_0001.HEIC IMG_0002.HEIC --format jpg

    # Whole folder, letter-size pages with margins
    python heic_convert.py ~/Pictures/trip -o trip.pdf --page letter
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

register_heif_opener()

HEIC_SUFFIXES = {".heic", ".heif", ".hif"}
IMAGE_SUFFIXES = HEIC_SUFFIXES | {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".avif",
}

# Page sizes in points (1/72 inch), portrait.
PAGE_SIZES = {
    "letter": (612, 792),
    "a4": (595, 842),
}
DPI = 150


def collect_inputs(paths):
    files = []
    for raw in paths:
        path = Path(raw).expanduser()
        if path.is_dir():
            files.extend(
                sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
            )
        elif path.is_file():
            files.append(path)
        else:
            print(f"warning: {raw} not found, skipping", file=sys.stderr)
    return files


def load_image(path):
    """Open an image, apply its EXIF rotation, and return it as RGB."""
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        return img.convert("RGB")


def fit_on_page(img, page, margin_in):
    """Place img centered on a white page of the given size, keeping aspect ratio."""
    width_pt, height_pt = PAGE_SIZES[page]
    if img.width > img.height:
        width_pt, height_pt = height_pt, width_pt  # landscape page for landscape photos
    page_w = round(width_pt / 72 * DPI)
    page_h = round(height_pt / 72 * DPI)
    margin = round(margin_in * DPI)
    box = (page_w - 2 * margin, page_h - 2 * margin)

    fitted = ImageOps.contain(img, box, Image.LANCZOS)
    canvas = Image.new("RGB", (page_w, page_h), "white")
    canvas.paste(fitted, ((page_w - fitted.width) // 2, (page_h - fitted.height) // 2))
    return canvas


def to_pdf(files, output, page, margin, quality):
    pages = []
    for path in files:
        img = load_image(path)
        pages.append(fit_on_page(img, page, margin) if page != "original" else img)
        print(f"added {path.name}")
    first, rest = pages[0], pages[1:]
    first.save(output, "PDF", save_all=True, append_images=rest, resolution=DPI, quality=quality)
    print(f"wrote {output} ({len(pages)} page{'s' if len(pages) != 1 else ''})")


def to_images(files, fmt, outdir, quality):
    for path in files:
        target_dir = outdir or path.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{path.stem}.{fmt}"
        if target.resolve() == path.resolve():
            target = target_dir / f"{path.stem}-converted.{fmt}"
        img = load_image(path)
        if fmt == "jpg":
            img.save(target, "JPEG", quality=quality)
        elif fmt == "webp":
            img.save(target, "WEBP", quality=quality)
        else:
            img.save(target, "PNG")
        print(f"wrote {target}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert HEIC (or any common image) to JPG/PNG/WebP, or combine images into a PDF."
    )
    parser.add_argument("inputs", nargs="+", help="image files, or folders containing them")
    parser.add_argument(
        "--format",
        choices=["pdf", "jpg", "png", "webp"],
        help="output type (default: pdf if -o ends in .pdf, otherwise jpg)",
    )
    parser.add_argument("-o", "--output", help="PDF file to write, or folder for jpg/png/webp output")
    parser.add_argument(
        "--page",
        choices=["original", "letter", "a4"],
        default="original",
        help="PDF page size; 'original' makes each page the photo's own size (default)",
    )
    parser.add_argument(
        "--margin", type=float, default=0.5, help="margin in inches for letter/a4 pages (default 0.5)"
    )
    parser.add_argument("--quality", type=int, default=90, help="JPEG quality 1-100 (default 90)")
    args = parser.parse_args(argv)

    files = collect_inputs(args.inputs)
    if not files:
        parser.error("no images found")

    fmt = args.format or ("pdf" if args.output and args.output.lower().endswith(".pdf") else "jpg")

    if fmt == "pdf":
        output = Path(args.output or "converted.pdf")
        to_pdf(files, output, args.page, args.margin, args.quality)
    else:
        outdir = Path(args.output) if args.output else None
        to_images(files, fmt, outdir, args.quality)


if __name__ == "__main__":
    main()
