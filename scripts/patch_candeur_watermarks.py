#!/usr/bin/env python3
"""
patch_candeur_watermarks.py
Removes:
1. "Galaxy Note20 Ultra 5G" camera watermark on Candeur Skyline day photo.
2. Blurry text smudge and white logo glyph on Candeur Skyline night photo.
Uses groove-aligned texture cloning with sub-pixel groove matching.
Regenerates master JPEGs and all WebP variants (full and 800w).
"""

import cv2
import numpy as np
from PIL import Image

def patch_day_image(img_path):
    img = cv2.imread(img_path)
    fh, fw = img.shape[:2]
    
    # In day image (960 x 1280):
    # crop y_offset = 710 (fh - 250)
    # Target: dst_y0 = 866, dst_y1 = 906 (h = 40)
    # Source: src_y0 = 904, src_y1 = 944 (h = 40)
    # dst_x: 50..360 (w = 310)
    # src_x: 67..377 (dx = -17)
    dst_y0, dst_y1 = 866, 906
    src_y0, src_y1 = 904, 944
    h = dst_y1 - dst_y0
    
    dst_x0, dst_x1 = 50, 360
    w = dst_x1 - dst_x0
    dx = -17
    src_x0 = dst_x0 - dx
    src_x1 = dst_x1 - dx
    
    patch = img[src_y0:src_y1, src_x0:src_x1].copy().astype(np.float32)
    
    alpha = np.ones((h, w, 1), dtype=np.float32)
    feather = 3
    alpha[:feather, :] = np.linspace(0, 1, feather)[:, None, None]
    alpha[-feather:, :] = np.linspace(1, 0, feather)[:, None, None]
    alpha[:, :feather] *= np.linspace(0, 1, feather)[None, :, None]
    alpha[:, -feather:] *= np.linspace(1, 0, feather)[None, :, None]
    
    out = img.copy()
    orig = out[dst_y0:dst_y1, dst_x0:dst_x1].astype(np.float32)
    blended = patch * alpha + orig * (1.0 - alpha)
    out[dst_y0:dst_y1, dst_x0:dst_x1] = np.clip(blended, 0, 255).astype(np.uint8)
    return out

def patch_night_image(img_path):
    img = cv2.imread(img_path)
    
    # 1. Patch the blurry text smudge:
    # Target: y=1370..1445, x=145..560
    y_t0_text, y_t1_text = 1370, 1445
    h_text = y_t1_text - y_t0_text
    x_t0_text, x_t1_text = 145, 560
    w_text = x_t1_text - x_t0_text
    
    y_s0_text = y_t0_text - 100
    y_s1_text = y_s0_text + h_text
    x_s0_text = x_t0_text + 85
    x_s1_text = x_s0_text + w_text
    
    patch_text = img[y_s0_text:y_s1_text, x_s0_text:x_s1_text].copy().astype(np.float32)
    top_diff_t = img[y_t0_text-2:y_t0_text, x_t0_text:x_t1_text].mean(axis=(0,1)) - patch_text[0:2, :].mean(axis=(0,1))
    bot_diff_t = img[y_t1_text:y_t1_text+2, x_t0_text:x_t1_text].mean(axis=(0,1)) - patch_text[-2:, :].mean(axis=(0,1))
    ramp_t = np.linspace(top_diff_t, bot_diff_t, h_text)[:, np.newaxis, :]
    patch_text += ramp_t
    patch_text = np.clip(patch_text, 0, 255)
    
    mask_text = np.ones((h_text, w_text), dtype=np.float32)
    for i in range(6):
        mask_text[i, :] *= (i / 6)
        mask_text[h_text-1-i, :] *= (i / 6)
    for j in range(12):
        mask_text[:, j] *= (j / 12)
        mask_text[:, w_text-1-j] *= (j / 12)
    mask_text = mask_text[:, :, np.newaxis]
    
    out = img.copy()
    blended_text = (patch_text * mask_text + out[y_t0_text:y_t1_text, x_t0_text:x_t1_text].astype(np.float32) * (1 - mask_text)).astype(np.uint8)
    out[y_t0_text:y_t1_text, x_t0_text:x_t1_text] = blended_text
    
    # 2. Patch the white logo glyph:
    # Target: y=1355..1465, x=55..145
    y_t0_logo, y_t1_logo = 1355, 1465
    h_logo = y_t1_logo - y_t0_logo
    x_t0_logo, x_t1_logo = 55, 145
    w_logo = x_t1_logo - x_t0_logo
    
    x_s0_logo = x_t0_logo + 90
    x_s1_logo = x_s0_logo + w_logo
    
    patch_logo = out[1245:1355, x_s0_logo:x_s1_logo].copy().astype(np.float32)
    top_diff_l = out[y_t0_logo-2:y_t0_logo, x_t0_logo:x_t1_logo].mean(axis=(0,1)) - patch_logo[0:2, :].mean(axis=(0,1))
    bot_diff_l = out[y_t1_logo:y_t1_logo+2, x_t0_logo:x_t1_logo].mean(axis=(0,1)) - patch_logo[-2:, :].mean(axis=(0,1))
    ramp_l = np.linspace(top_diff_l, bot_diff_l, h_logo)[:, np.newaxis, :]
    patch_logo += ramp_l
    patch_logo = np.clip(patch_logo, 0, 255)
    
    mask_logo = np.ones((h_logo, w_logo), dtype=np.float32)
    for i in range(8):
        mask_logo[i, :] *= (i / 8)
        mask_logo[h_logo-1-i, :] *= (i / 8)
    for j in range(8):
        mask_logo[:, j] *= (j / 8)
        mask_logo[:, w_logo-1-j] *= (j / 8)
    mask_logo = mask_logo[:, :, np.newaxis]
    
    blended_logo = (patch_logo * mask_logo + out[y_t0_logo:y_t1_logo, x_t0_logo:x_t1_logo].astype(np.float32) * (1 - mask_logo)).astype(np.uint8)
    out[y_t0_logo:y_t1_logo, x_t0_logo:x_t1_logo] = blended_logo
    
    return out

def export_webp(bgr_img, out_path, target_width=None, quality=88):
    rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    if target_width and pil_img.width > target_width:
        target_height = int(pil_img.height * (target_width / pil_img.width))
        pil_img = pil_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    pil_img.save(out_path, 'WEBP', quality=quality, method=6)
    print(f'Wrote {out_path} ({pil_img.width}x{pil_img.height})')

def main():
    print('Processing Candeur day image...')
    day_patched = patch_day_image('assets/images/barricade-candeur-day.jpg')
    cv2.imwrite('assets/images/barricade-candeur-day.jpg', day_patched, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print('Updated assets/images/barricade-candeur-day.jpg')
    
    export_webp(day_patched, 'v2/img/barricade-candeur-day.webp', target_width=1600, quality=88)
    export_webp(day_patched, 'v2/img/barricade-candeur-day-800.webp', target_width=800, quality=88)
    
    print('Processing Candeur night image...')
    night_patched = patch_night_image('assets/images/barricade-candeur-night.jpg')
    cv2.imwrite('assets/images/barricade-candeur-night.jpg', night_patched, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print('Updated assets/images/barricade-candeur-night.jpg')
    
    export_webp(night_patched, 'v2/img/barricade-candeur-night.webp', target_width=1600, quality=88)
    export_webp(night_patched, 'v2/img/barricade-candeur-night-800.webp', target_width=800, quality=88)
    
    print('All Candeur images successfully patched and saved!')

if __name__ == '__main__':
    main()
