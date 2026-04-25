#!/usr/bin/env python3
import argparse
import os
from PIL import Image

def strip_metadata_to_jpg(input_path: str, output_path: str, quality: int = 95):
    """
    Load an image, drop all metadata, and save as a high‑quality JPEG.

    Args:
      input_path:  path to your source file (e.g. ~/Desktop/screen.png)
      output_path: desired .jpg output path
      quality:     JPEG quality (1–100), default 95
    """
    # 1. Open source image
    with Image.open(input_path) as src:
        # 2. Copy pixel data into a fresh image (this discards EXIF/metadata)
        clean = Image.new(src.mode, src.size)
        clean.putdata(list(src.getdata()))
        # 3. Convert to RGB (JPEG requirement) and save
        clean = clean.convert("RGB")
        clean.save(output_path, "JPEG", quality=quality, optimize=True)
        print(f"✅ Stripped metadata and saved as {output_path}")

def main():
    p = argparse.ArgumentParser(
        description="Strip metadata from an image and export as high‑quality JPEG"
    )
    p.add_argument("input", help="Path to source image (e.g. screenshot.png)")
    p.add_argument(
        "-o","--output",
        help="Output JPEG path (defaults to same name with .jpg)",
        default=None
    )
    p.add_argument(
        "-q","--quality",
        type=int,
        default=95,
        help="JPEG quality 1–100 (default 95)"
    )
    args = p.parse_args()

    inp = args.input
    if not os.path.isfile(inp):
        p.error(f"Input file not found: {inp}")

    out = args.output or os.path.splitext(inp)[0] + ".jpg"
    strip_metadata_to_jpg(inp, out, args.quality)

if __name__ == "__main__":
    main()

