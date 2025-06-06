import cv2
import numpy as np
from utils.analysis import (
    estimate_noise,
    has_color_cast,
    is_low_contrast,
    is_blurry,
    needs_saturation_boost
)

def denoise_bilateral(img, sigma_space=3, sigma_color=60):
    """Terapkan bilateral filter untuk denoising ringan"""
    return cv2.bilateralFilter(img, d=9, sigmaColor=sigma_color, sigmaSpace=sigma_space)

def denoise_nlm(img):
    """Terapkan Non-Local Means untuk noise berat"""
    return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

def white_balance_grayworld(img, r_gain=1.0, g_gain=1.0, b_gain=1.0):
    """Koreksi white balance menggunakan Gray-World Assumption"""
    b, g, r = cv2.split(img.astype(np.float32))
    b *= b_gain
    g *= g_gain
    r *= r_gain
    result = cv2.merge((b, g, r))
    return np.clip(result, 0, 255).astype(np.uint8)

def auto_white_balance_grayworld(img):
    """Auto-koreksi white balance jika color cast terdeteksi"""
    b, g, r = cv2.split(img.astype(np.float32))
    avg_b, avg_g, avg_r = np.mean(b), np.mean(g), np.mean(r)
    avg_gray = (avg_b + avg_g + avg_r) / 3
    b_gain = avg_gray / avg_b
    g_gain = avg_gray / avg_g
    r_gain = avg_gray / avg_r
    return white_balance_grayworld(img, r_gain, g_gain, b_gain)

def enhance_contrast_clahe(img, clip_limit=2.0, tile_grid=8):
    """Terapkan CLAHE pada channel L atau V (jika HSV)"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid, tile_grid))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

def enhance_contrast_histogram(img):
    """Alternatif kontras: histogram equalization global (grayscale)"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    eq = cv2.equalizeHist(gray)
    return cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)

def enhance_saturation(img, scale=1.1):
    """Tingkatkan saturasi pada channel HSV"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = cv2.split(hsv)
    s *= scale
    s = np.clip(s, 0, 255)
    enhanced = cv2.merge((h, s, v))
    return cv2.cvtColor(enhanced.astype(np.uint8), cv2.COLOR_HSV2BGR)

def unsharp_masking(img, radius=1.0, amount=100):
    """Terapkan penajaman dengan unsharp masking"""
    blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=radius)
    sharpened = cv2.addWeighted(img, 1 + (amount / 100.0), blurred, -(amount / 100.0), 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)

def auto_enhance(img):
    """Enhancement otomatis berurutan: Denoising → WB → Kontras → Saturasi → Sharpen"""
    result = img.copy()

    # 1. Denoising
    noise_std = estimate_noise(result)
    if noise_std > 10:
        if noise_std > 25:
            result = denoise_nlm(result)
        else:
            result = denoise_bilateral(result, sigma_space=3, sigma_color=2*noise_std)

    # 2. White Balance
    if has_color_cast(result):
        result = auto_white_balance_grayworld(result)

    # 3. Kontras
    if is_low_contrast(result):
        result = enhance_contrast_clahe(result, clip_limit=2.0, tile_grid=8)

    # 4. Saturasi
    if needs_saturation_boost(result):
        result = enhance_saturation(result, scale=1.1)

    # 5. Sharpening
    if is_blurry(result):
        result = unsharp_masking(result, radius=1.0, amount=100)

    return result
