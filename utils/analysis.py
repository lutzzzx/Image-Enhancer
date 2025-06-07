import cv2
import numpy as np

# ================= ANALYSIS FUNCTIONS =================

def estimate_noise(img):
    """
    Estimasi noise dengan menghitung standar deviasi intensitas 
    pada area datar (menggunakan Gaussian blur subtraction).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    noise = gray.astype(np.float32) - blur.astype(np.float32)
    std_dev = np.std(noise)
    return std_dev

def analyze_brightness(img):
    """Analisis tingkat kecerahan gambar"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    return mean_brightness

def analyze_dynamic_range(img):
    """Analisis dynamic range gambar"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0,256])
    hist_norm = hist.ravel() / hist.sum()
    cum_hist = np.cumsum(hist_norm)
    
    # Hitung rentang dinamis
    low_1 = np.searchsorted(cum_hist, 0.01)
    high_99 = np.searchsorted(cum_hist, 0.99)
    low_5 = np.searchsorted(cum_hist, 0.05)
    high_95 = np.searchsorted(cum_hist, 0.95)
    
    dynamic_range_99 = high_99 - low_1
    dynamic_range_95 = high_95 - low_5
    
    return {
        'range_99': dynamic_range_99,
        'range_95': dynamic_range_95,
        'low_1': low_1,
        'high_99': high_99,
        'low_5': low_5,
        'high_95': high_95
    }

def has_color_cast(img, threshold=15):
    """Deteksi color cast dan hitung tingkat severity"""
    b, g, r = cv2.split(img)
    mean_b, mean_g, mean_r = np.mean(b), np.mean(g), np.mean(r)
    
    max_diff = max(abs(mean_r - mean_g), abs(mean_g - mean_b), abs(mean_b - mean_r))
    severity = max_diff / 255.0  # Normalisasi ke 0-1
    
    return {
        'has_cast': max_diff > threshold,
        'severity': severity,
        'means': (mean_r, mean_g, mean_b)
    }

def is_low_contrast(img, threshold=0.3):
    """Analisis kontras dengan berbagai metrik"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Metode 1: Range-based contrast
    hist = cv2.calcHist([gray], [0], None, [256], [0,256])
    hist_norm = hist.ravel() / hist.sum()
    cum_hist = np.cumsum(hist_norm)
    
    low = np.searchsorted(cum_hist, 0.01)
    high = np.searchsorted(cum_hist, 0.99)
    contrast_ratio = (high - low) / 255.0
    
    # Metode 2: Standard deviation contrast
    std_contrast = np.std(gray) / 255.0
    
    # Metode 3: RMS contrast
    rms_contrast = np.sqrt(np.mean((gray - np.mean(gray))**2)) / 255.0
    
    return {
        'is_low': contrast_ratio < threshold,
        'range_contrast': contrast_ratio,
        'std_contrast': std_contrast,
        'rms_contrast': rms_contrast
    }

def needs_saturation_boost(img, threshold=60):
    """Analisis saturasi dengan detail level"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1]
    
    mean_saturation = np.mean(s)
    std_saturation = np.std(s)
    
    # Hitung persentase pixel dengan saturasi rendah
    low_sat_pixels = np.sum(s < 50) / s.size
    
    return {
        'needs_boost': mean_saturation < threshold,
        'mean_sat': mean_saturation,
        'std_sat': std_saturation,
        'low_sat_ratio': low_sat_pixels
    }

def is_blurry(img, threshold=100.0):
    """Analisis blur dengan multiple metrics"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Metode 1: Variance of Laplacian
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Metode 2: Gradient magnitude
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    mean_gradient = np.mean(grad_magnitude)
    
    return {
        'is_blurry': laplacian_var < threshold,
        'laplacian_var': laplacian_var,
        'mean_gradient': mean_gradient,
        'blur_severity': max(0, 1 - (laplacian_var / threshold))
    }