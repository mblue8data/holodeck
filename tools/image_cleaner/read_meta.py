#!/usr/bin/env python3
import argparse
from PIL import Image
from PIL.ExifTags import TAGS

def print_metadata(path: str):
    """
    Open an image, print its PIL info dict and, if present,
    decode & print EXIF tags (raw bytes + human‑readable).
    """
    img = Image.open(path)

    # 1. Pillow info dict (PNG text chunks, basic fields)
    print(f"\nPIL info dict for {path}:")
    for k, v in img.info.items():
        print(f"  {k}: {v!r}")

    # 2. Raw EXIF bytes (JPEGs only)
    exif_bytes = img.info.get("exif")
    if not exif_bytes:
        print("\nNo EXIF data found.")
        return

    print("\nRaw EXIF bytes present (length: {} bytes).".format(len(exif_bytes)))
    try:
        exif_dict = img._getexif() or {}
    except Exception as e:
        print(f"  ⚠️  Could not parse EXIF: {e}")
        return

    # 3. Human‑readable EXIF tags
    print("\nDecoded EXIF tags:")
    for tag_id, value in exif_dict.items():
        name = TAGS.get(tag_id, tag_id)
        print(f"  {name}: {value!r}")

def main():
    p = argparse.ArgumentParser(
        description="Read and display image metadata (PNG info + JPEG EXIF)."
    )
    p.add_argument(
        "file",
        help="Path to the image file (PNG, JPEG, etc.)"
    )
    args = p.parse_args()
    print_metadata(args.file)

if __name__ == "__main__":
    main()

