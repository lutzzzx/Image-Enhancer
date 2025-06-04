import cv2
import numpy as np
from utils.analysis import (
    is_noisy, get_noise_sigma,
    has_color_cast,
    is_low_contrast,
    is_low_saturation,
    needs_sharpening
)

# === Helper Enhancement Functions ===

def denoise_image(img, sigma_space=3, sigma_color=60):
    return cv2.bilateralFilter(img, d=0, sigmaColor=sigma_color, sigmaSpace=sigma_space)

def non_local_means_denoise(img):
    return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

def apply_gray_world(img):
    avg_b, avg_g, avg_r = np.mean(img[:, :, 0]), np.mean(img[:, :, 1]), np.mean(img[:, :, 2])
    avg_gray = (avg_r + avg_g + avg_b) / 3
    scale = [avg_gray / avg_b, avg_gray / avg_g, avg_gray / avg_r]
    result = cv2.merge([cv2.multiply(img[:, :, c], scale[c]) for c in range(3)])
    return np.clip(result, 0, 255).astype(np.uint8)

def apply_clahe(img, clip_limit=2.0, tile_grid_size=(8, 8)):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    l_clahe = clahe.apply(l)
    merged = cv2.merge((l_clahe, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

def increase_saturation(img, factor=1.2):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] *= factor
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

def sharpen_image(img, radius=1.0, amount=100):
    blurred = cv2.GaussianBlur(img, (0, 0), radius)
    sharpened = cv2.addWeighted(img, 1 + amount / 100.0, blurred, -amount / 100.0, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)

# === Automatic Enhancement ===

def enhance_automatic(input_path, output_path):
    img = cv2.imread(input_path)
    sigma = get_noise_sigma(img)

    # 1. Denoising
    if is_noisy(img, threshold=20):
        if sigma > 25:
            img = non_local_means_denoise(img)
        else:
            img = denoise_image(img, sigma_space=3, sigma_color=2 * sigma)

    # 2. White Balance
    if has_color_cast(img, threshold=10):
        img = apply_gray_world(img)

    # 3. Kontras / Tonality
    if is_low_contrast(img, threshold=0.15):
        img = apply_clahe(img, clip_limit=2.0, tile_grid_size=(8, 8))

    # 4. Saturasi
    if is_low_saturation(img, threshold=0.25):
        img = increase_saturation(img, factor=1.2)

    # 5. Sharpening
    if needs_sharpening(img, threshold=50.0):
        img = sharpen_image(img, radius=1.0, amount=100)

    cv2.imwrite(output_path, img)

# === Manual Enhancement ===

def enhance_manual(input_path, output_path, params):
    img = cv2.imread(input_path)

    # 1. Denoise
    img = denoise_image(img, sigma_space=params['sigma_space'], sigma_color=params['sigma_color'])

    # 2. White Balance
    img = apply_white_balance_gain(img, params['r_gain'], params['g_gain'], params['b_gain'])

    # 3. CLAHE
    img = apply_clahe(img, clip_limit=params['clip_limit'],
                      tile_grid_size=(params['tile_grid'], params['tile_grid']))

    # 4. Saturation
    img = increase_saturation(img, factor=params['saturation'])

    # 5. Sharpening
    img = sharpen_image(img, radius=params['sharpen_radius'], amount=params['sharpen_amount'])

    cv2.imwrite(output_path, img)

# === Manual White Balance Helper ===

def apply_white_balance_gain(img, r_gain=1.0, g_gain=1.0, b_gain=1.0):
    b, g, r = cv2.split(img)
    b = np.clip(b * b_gain, 0, 255).astype(np.uint8)
    g = np.clip(g * g_gain, 0, 255).astype(np.uint8)
    r = np.clip(r * r_gain, 0, 255).astype(np.uint8)
    return cv2.merge([b, g, r])
