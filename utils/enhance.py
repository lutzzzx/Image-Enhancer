import cv2
import numpy as np
from utils.analysis import (
    estimate_noise,
    has_color_cast,
    is_low_contrast,
    is_blurry,
    analyze_brightness,
    analyze_dynamic_range,
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


def adaptive_denoise_bilateral(img, noise_std):
    """Bilateral filter dengan parameter adaptif"""
    # Parameter adaptif berdasarkan noise level
    if noise_std < 5:
        d, sigma_color, sigma_space = 5, 30, 30
    elif noise_std < 15:
        d, sigma_color, sigma_space = 7, 50, 50
    elif noise_std < 25:
        d, sigma_color, sigma_space = 9, 70, 70
    else:
        d, sigma_color, sigma_space = 11, 90, 90
    
    return cv2.bilateralFilter(img, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)

def adaptive_denoise_nlm(img, noise_std):
    """Non-Local Means dengan parameter adaptif"""
    # Parameter berdasarkan tingkat noise
    if noise_std < 20:
        h, template_window, search_window = 8, 7, 21
    elif noise_std < 35:
        h, template_window, search_window = 12, 7, 21
    else:
        h, template_window, search_window = 15, 9, 25
    
    return cv2.fastNlMeansDenoisingColored(img, None, h, h, template_window, search_window)

def adaptive_white_balance(img, cast_info):
    """White balance adaptif berdasarkan severity color cast"""
    if not cast_info['has_cast']:
        return img
    
    severity = cast_info['severity']
    mean_r, mean_g, mean_b = cast_info['means']
    
    # Hitung gain dengan smoothing factor berdasarkan severity
    avg_gray = (mean_b + mean_g + mean_r) / 3
    
    # Smoothing factor: semakin tinggi severity, semakin agresif koreksi
    smooth_factor = 0.3 + (severity * 0.7)  # 0.3 - 1.0
    
    b_gain = avg_gray / max(mean_b, 1e-6)  # Avoid division by zero
    g_gain = avg_gray / max(mean_g, 1e-6)
    r_gain = avg_gray / max(mean_r, 1e-6)
    
    # Apply smoothing
    b_gain = 1 + (b_gain - 1) * smooth_factor
    g_gain = 1 + (g_gain - 1) * smooth_factor
    r_gain = 1 + (r_gain - 1) * smooth_factor
    
    # Limit extreme corrections
    b_gain = np.clip(b_gain, 0.5, 2.0)
    g_gain = np.clip(g_gain, 0.5, 2.0)
    r_gain = np.clip(r_gain, 0.5, 2.0)
    
    # Apply white balance with proper data type handling
    img_float = img.astype(np.float32)
    b, g, r = cv2.split(img_float)
    
    b *= b_gain
    g *= g_gain
    r *= r_gain
    
    # Ensure all channels have same data type
    b = np.clip(b, 0, 255).astype(np.float32)
    g = np.clip(g, 0, 255).astype(np.float32)
    r = np.clip(r, 0, 255).astype(np.float32)
    
    result = cv2.merge((b, g, r))
    return result.astype(np.uint8)

def adaptive_contrast_clahe(img, contrast_info, brightness):
    """CLAHE dengan parameter adaptif"""
    if not contrast_info['is_low']:
        return img
    
    contrast_level = contrast_info['range_contrast']
    std_contrast = contrast_info['std_contrast']
    
    # Adaptive clip limit berdasarkan kontras dan brightness
    base_clip_limit = 2.0
    
    # Tingkatkan clip limit untuk gambar kontras sangat rendah
    if contrast_level < 0.15:
        clip_limit = base_clip_limit * 2.5
    elif contrast_level < 0.25:
        clip_limit = base_clip_limit * 1.8
    else:
        clip_limit = base_clip_limit * 1.2
    
    # Adjust berdasarkan brightness
    if brightness < 80:  # Dark image
        clip_limit *= 1.3
    elif brightness > 180:  # Bright image
        clip_limit *= 0.8
    
    # Adaptive tile size
    tile_size = 8
    if std_contrast < 0.1:  # Very uniform image
        tile_size = 6  # Smaller tiles for more local adaptation
    elif std_contrast > 0.2:  # High variation
        tile_size = 12  # Larger tiles for smoother result
    
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    cl = clahe.apply(l)
    
    # Ensure all channels have same data type
    cl = cl.astype(np.uint8)
    a = a.astype(np.uint8)
    b = b.astype(np.uint8)
    
    # Merge channels back
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

def adaptive_saturation_enhancement(img, sat_info):
    """Peningkatan saturasi adaptif"""
    if not sat_info['needs_boost']:
        return img
    
    mean_sat = sat_info['mean_sat']
    low_sat_ratio = sat_info['low_sat_ratio']
    
    # Hitung scale factor berdasarkan kondisi
    if mean_sat < 30:  # Very desaturated
        scale = 1.4 + (low_sat_ratio * 0.3)
    elif mean_sat < 50:  # Moderately desaturated
        scale = 1.2 + (low_sat_ratio * 0.2)
    else:  # Slightly desaturated
        scale = 1.1 + (low_sat_ratio * 0.1)
    
    # Limit maximum enhancement
    scale = min(scale, 1.8)
    
    # Convert to HSV with proper data type handling
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_float = hsv.astype(np.float32)
    h, s, v = cv2.split(hsv_float)
    
    # Apply saturation enhancement with proper scaling
    s_enhanced = s * scale
    s_enhanced = np.clip(s_enhanced, 0, 255)
    
    # Ensure all channels have the same data type and shape
    h = h.astype(np.float32)
    s_enhanced = s_enhanced.astype(np.float32)
    v = v.astype(np.float32)
    
    # Merge channels
    enhanced_hsv = cv2.merge((h, s_enhanced, v))
    enhanced_hsv = enhanced_hsv.astype(np.uint8)
    
    return cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)

def adaptive_unsharp_masking(img, blur_info, noise_std):
    """Unsharp masking adaptif"""
    if not blur_info['is_blurry']:
        return img
    
    blur_severity = blur_info['blur_severity']
    laplacian_var = blur_info['laplacian_var']
    
    # Parameter adaptif berdasarkan blur severity dan noise
    if blur_severity > 0.7:  # Very blurry
        radius = 1.5
        amount = 120
    elif blur_severity > 0.4:  # Moderately blurry
        radius = 1.2
        amount = 100
    else:  # Slightly blurry
        radius = 0.8
        amount = 80
    
    # Reduce sharpening jika ada noise tinggi
    if noise_std > 15:
        amount *= 0.7
        radius *= 1.2  # Use wider radius for smoother result
    elif noise_std > 25:
        amount *= 0.5
        radius *= 1.5
    
    # Limit parameters
    radius = max(0.5, min(radius, 2.0))
    amount = max(20, min(amount, 150))
    
    # Apply unsharp masking with proper data type handling
    img_float = img.astype(np.float32)
    blurred = cv2.GaussianBlur(img_float, (0, 0), sigmaX=radius)
    
    # Calculate the sharpened image
    sharpened = img_float + (amount / 100.0) * (img_float - blurred)
    
    # Clip and convert back to uint8
    sharpened = np.clip(sharpened, 0, 255)
    
    return sharpened.astype(np.uint8)

    sharpened = cv2.addWeighted(img, 1 + (amount / 100.0), blurred, -(amount / 100.0), 0)
    
    return np.clip(sharpened, 0, 255).astype(np.uint8)

def gamma_correction_adaptive(img, brightness, dynamic_range_info):
    """Gamma correction adaptif berdasarkan brightness dan dynamic range"""
    # Hitung gamma berdasarkan brightness
    if brightness < 60:  # Very dark
        gamma = 0.6
    elif brightness < 100:  # Dark
        gamma = 0.8
    elif brightness > 180:  # Very bright
        gamma = 1.4
    elif brightness > 140:  # Bright
        gamma = 1.2
    else:  # Normal
        return img
    
    # Adjust gamma berdasarkan dynamic range
    dr_95 = dynamic_range_info['range_95']
    if dr_95 < 100:  # Low dynamic range
        gamma = gamma * 0.9  # Less aggressive correction
    
    # Apply gamma correction
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype(np.uint8)
    
    return cv2.LUT(img, table)

def auto_enhance(img):
    """
    Enhancement otomatis dengan parameter adaptif penuh
    """
    result = img.copy()
    
    try:
        # Analisis gambar
        noise_std = estimate_noise(result)
        brightness = analyze_brightness(result)
        dynamic_range_info = analyze_dynamic_range(result)
        cast_info = has_color_cast(result)
        contrast_info = is_low_contrast(result)
        sat_info = needs_saturation_boost(result)
        blur_info = is_blurry(result)
        
        print(f"Image Analysis:")
        print(f"- Noise STD: {noise_std:.2f}")
        print(f"- Brightness: {brightness:.1f}")
        print(f"- Dynamic Range (95%): {dynamic_range_info['range_95']}")
        print(f"- Color Cast Severity: {cast_info['severity']:.3f}")
        print(f"- Contrast (Range): {contrast_info['range_contrast']:.3f}")
        print(f"- Mean Saturation: {sat_info['mean_sat']:.1f}")
        print(f"- Blur Severity: {blur_info['blur_severity']:.3f}")
        print("-" * 50)
        
        # 1. Gamma Correction (jika diperlukan untuk brightness)
        result = gamma_correction_adaptive(result, brightness, dynamic_range_info)
        
        # 2. Denoising
        if noise_std > 8:
            print(f"Applying denoising (noise_std: {noise_std:.2f})")
            if noise_std > 25:
                result = adaptive_denoise_nlm(result, noise_std)
            else:
                result = adaptive_denoise_bilateral(result, noise_std)
        
        # 3. White Balance
        if cast_info['has_cast']:
            print(f"Applying white balance (severity: {cast_info['severity']:.3f})")
            result = adaptive_white_balance(result, cast_info)
            # Re-analyze after white balance
            brightness = analyze_brightness(result)
        
        # 4. Contrast Enhancement
        if contrast_info['is_low']:
            print(f"Applying contrast enhancement (range: {contrast_info['range_contrast']:.3f})")
            result = adaptive_contrast_clahe(result, contrast_info, brightness)
        
        # 5. Saturation Enhancement
        if sat_info['needs_boost']:
            print(f"Applying saturation boost (mean_sat: {sat_info['mean_sat']:.1f})")
            result = adaptive_saturation_enhancement(result, sat_info)
        
        # 6. Sharpening (terakhir)
        if blur_info['is_blurry']:
            print(f"Applying sharpening (blur_severity: {blur_info['blur_severity']:.3f})")
            result = adaptive_unsharp_masking(result, blur_info, noise_std)
        
        return result
    
    except Exception as e:
        print(f"Error in auto_enhance_adaptive: {str(e)}")
        print("Returning original image")
        return img
