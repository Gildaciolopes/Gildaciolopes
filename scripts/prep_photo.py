#!/usr/bin/env python3
"""Prep a photo for ASCII conversion.

Pipeline (run once per photo):
  1. Remove background with rembg -> subject isolated on transparency.
  2. Composite onto pure white so the background maps to the blank end of
     the ASCII ramp (white -> spaces).
  3. Boost local contrast with OpenCV CLAHE so a flatly-lit face gets real
     highlights and shadows instead of a dark blob.

Output: source-prepped.png (grayscale).

Usage:
    python scripts/prep_photo.py assets/professional-image.png
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT = "source-prepped.png"


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else "assets/professional-image.png"
    print(f"[prep] input: {src}")

    # 1. remove background
    fg = remove(Image.open(src).convert("RGBA"))

    # 2. composite onto pure white
    white = Image.new("RGBA", fg.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(white, fg).convert("L")  # grayscale

    # 3. CLAHE local contrast
    arr = np.array(comp)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    arr = clahe.apply(arr)

    # keep the background pure white: rembg alpha == 0 -> force 255
    alpha = np.array(fg.split()[-1])
    arr[alpha == 0] = 255

    Image.fromarray(arr).save(OUT)
    print(f"[prep] wrote {OUT} ({comp.size[0]}x{comp.size[1]})")


if __name__ == "__main__":
    main()
