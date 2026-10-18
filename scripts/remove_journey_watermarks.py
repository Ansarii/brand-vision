#!/usr/bin/env python3
"""
Remove camera date/time watermarks from airport journey photos:
1. airport-gate-jackdaniels: date stamp "18 01 2023" at y=[866, 898], x=[1313, 1511]
2. airport-baggage-sumadhura: date stamp "01 03 2025" at y=[967, 995], x=[1360, 1583]

Uses dilated color-boundary masking, Telea inpainting, and high-frequency texture injection
to eliminate watermarks with zero blur and zero ghost outlines.
Generates full-res master JPGs and high-quality WebP (1600w and 800w) assets.
"""

import os
import cv2
import numpy as np
from PIL import Image

def clean_jackdaniels():
    path = "assets/images/airport-gate-jackdaniels.jpg"
    print(f"Cleaning {path}...")
    img = cv2.imread(path)
    h, w, c = img.shape

    # Pre-clean the 1px white border artifact at row 898-899
    img[898:] = img[896:897]

    # Detect orange stamp
    b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    orange = (r > 150) & (g > 50) & (g < 190) & (b < 120)
    sub = np.zeros((h, w), dtype=bool)
    sub[860:900, 1300:1520] = True

    mask = (orange & sub).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    dilated = cv2.dilate(mask, kernel, iterations=2)

    # Inpaint
    inpainted = cv2.inpaint(img, dilated, 4, cv2.INPAINT_TELEA)

    # Clean floor patch from 38px above
    clean_patch = img[860-38:900-38, 1300:1520]
    clean_lowpass = cv2.GaussianBlur(clean_patch, (5, 5), 0)
    high_freq = clean_patch.astype(np.float32) - clean_lowpass.astype(np.float32)

    target_crop = inpainted[860:900, 1300:1520].astype(np.float32)
    mask_crop = (dilated[860:900, 1300:1520] > 0)[:, :, None].astype(np.float32)
    mask_crop = cv2.GaussianBlur(mask_crop, (3, 3), 0)[:, :, None]
    restored = np.clip(target_crop + high_freq * mask_crop * 1.1, 0, 255).astype(np.uint8)

    res = inpainted.copy()
    res[860:900, 1300:1520] = restored

    # Overwrite master JPG
    cv2.imwrite(path, res, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"  Updated master {path}")

    # Export WebP (1600w and 800w)
    res_rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(res_rgb)

    out_full = "v2/img/airport-gate-jackdaniels.webp"
    pil_img.save(out_full, "WEBP", quality=90, method=6)
    print(f"  Generated {out_full} ({os.path.getsize(out_full)} bytes)")

    out_800 = "v2/img/airport-gate-jackdaniels-800.webp"
    w800 = 800
    h800 = int(round(h * (w800 / w)))
    pil_800 = pil_img.resize((w800, h800), Image.Resampling.LANCZOS)
    pil_800.save(out_800, "WEBP", quality=88, method=6)
    print(f"  Generated {out_800} ({os.path.getsize(out_800)} bytes)")


def clean_sumadhura():
    path = "assets/images/airport-baggage-sumadhura.jpg"
    print(f"Cleaning {path}...")
    img = cv2.imread(path)
    h, w, c = img.shape

    # Detect orange stamp
    b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    orange = (r > 155) & (g > 55) & (g < 195) & (b < 115)
    sub = np.zeros((h, w), dtype=bool)
    sub[960:1005, 1350:1590] = True

    mask = (orange & sub).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    dilated = cv2.dilate(mask, kernel, iterations=2)

    # Inpaint
    inpainted = cv2.inpaint(img, dilated, 4, cv2.INPAINT_TELEA)

    # HF texture injection from carpet 45px above
    clean_patch = img[960-45:1005-45, 1350:1590]
    clean_lowpass = cv2.GaussianBlur(clean_patch, (7, 7), 0)
    high_freq = clean_patch.astype(np.float32) - clean_lowpass.astype(np.float32)

    target_crop = inpainted[960:1005, 1350:1590].astype(np.float32)
    mask_crop = (dilated[960:1005, 1350:1590] > 0)[:, :, None].astype(np.float32)
    mask_crop = cv2.GaussianBlur(mask_crop, (5, 5), 0)[:, :, None]
    restored = np.clip(target_crop + high_freq * mask_crop * 1.3, 0, 255).astype(np.uint8)

    res = inpainted.copy()
    res[960:1005, 1350:1590] = restored

    # Overwrite master JPG
    cv2.imwrite(path, res, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"  Updated master {path}")

    # Export WebP (1600w and 800w)
    res_rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(res_rgb)

    out_full = "v2/img/airport-baggage-sumadhura.webp"
    pil_img.save(out_full, "WEBP", quality=90, method=6)
    print(f"  Generated {out_full} ({os.path.getsize(out_full)} bytes)")

    out_800 = "v2/img/airport-baggage-sumadhura-800.webp"
    w800 = 800
    h800 = int(round(h * (w800 / w)))
    pil_800 = pil_img.resize((w800, h800), Image.Resampling.LANCZOS)
    pil_800.save(out_800, "WEBP", quality=88, method=6)
    print(f"  Generated {out_800} ({os.path.getsize(out_800)} bytes)")


if __name__ == "__main__":
    clean_jackdaniels()
    clean_sumadhura()
    print("All airport journey watermarks cleaned successfully.")
