import cv2
import numpy as np

def estimate_noise(img):
    """
    Estimasi noise dengan menghitung standar deviasi intensitas 
    pada area datar (menggunakan Gaussian blur subtraction).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    noise = gray.astype(np.float32) - blur.astype(np.float32)
    std_dev = np.std(noise)
    return std_dev  # Semakin tinggi, semakin noisy

def has_color_cast(img, threshold=15):
    """
    Deteksi color cast berdasarkan selisih rata-rata RGB.
    Jika selisih antara saluran RGB signifikan → white balance dibutuhkan.
    """
    b, g, r = cv2.split(img)
    mean_b, mean_g, mean_r = np.mean(b), np.mean(g), np.mean(r)
    max_diff = max(abs(mean_r - mean_g), abs(mean_g - mean_b), abs(mean_b - mean_r))
    return max_diff > threshold

def is_low_contrast(img, threshold=0.25):
    """
    Deteksi kontras rendah berdasarkan rasio distribusi histogram.
    Jika rentang intensitas hanya mencakup sebagian kecil spektrum (0-255).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0,256])
    hist_norm = hist.ravel() / hist.sum()
    cum_hist = np.cumsum(hist_norm)

    # Hitung rentang antara persentil 1% hingga 99%
    low = np.searchsorted(cum_hist, 0.01)
    high = np.searchsorted(cum_hist, 0.99)
    contrast_ratio = (high - low) / 255.0

    return contrast_ratio < threshold

def needs_saturation_boost(img, threshold=60):
    """
    Deteksi saturasi rendah berdasarkan nilai rata-rata saluran S di HSV.
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1]
    mean_saturation = np.mean(s)
    return mean_saturation < threshold

def is_blurry(img, threshold=100.0):
    """
    Deteksi blur dengan Variance of Laplacian.
    Semakin rendah varians → semakin blur.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold
