from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import uuid
from utils.enhance import (
    auto_enhance,
    denoise_bilateral,
    white_balance_grayworld,
    enhance_contrast_clahe,
    enhance_saturation,
    unsharp_masking
)
import numpy as np

# Inisialisasi Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload tersedia
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_image(image, suffix="enhanced"):
    """Simpan gambar ke folder upload dan kembalikan nama file baru"""
    filename = f"{uuid.uuid4().hex}_{suffix}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cv2.imwrite(filepath, image)
    return filename


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)

        # Simpan file asli
        filename = f"{uuid.uuid4().hex}_original.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        return render_template('index.html', filename=filename)

    return render_template('index.html', filename=None)


@app.route('/auto_enhance', methods=['POST'])
def auto_enhance_route():
    filename = request.form.get('filename')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(filepath)

    enhanced_img = auto_enhance(img)
    result_filename = save_image(enhanced_img, suffix="auto")

    return {'filename': result_filename}


@app.route('/manual_enhance', methods=['POST'])
def manual_enhance_route():
    data = request.json
    filename = data.get('filename')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(filepath)

    # Ambil parameter manual
    sigma_space = float(data.get('sigma_space', 3))
    sigma_color = float(data.get('sigma_color', 60))

    r_gain = float(data.get('r_gain', 1.0))
    g_gain = float(data.get('g_gain', 1.0))
    b_gain = float(data.get('b_gain', 1.0))

    clip_limit = float(data.get('clip_limit', 2.0))
    tile_grid = int(data.get('tile_grid', 8))

    saturation_scale = float(data.get('saturation', 1.1))

    sharpen_radius = float(data.get('sharpen_radius', 1.0))
    sharpen_amount = float(data.get('sharpen_amount', 100))

    # Jalankan fungsi manual enhancement
    img = denoise_bilateral(img, sigma_space, sigma_color)
    img = white_balance_grayworld(img, r_gain, g_gain, b_gain)
    img = enhance_contrast_clahe(img, clip_limit, tile_grid)
    img = enhance_saturation(img, saturation_scale)
    img = unsharp_masking(img, radius=sharpen_radius, amount=sharpen_amount)

    result_filename = save_image(img, suffix="manual")

    return {'filename': result_filename}


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
