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

def remove_all_enhanced_images():
    """Hapus semua file *_auto.jpg dan *_manual.jpg dari folder upload"""
    folder = app.config['UPLOAD_FOLDER']
    for fname in os.listdir(folder):
        if fname.endswith('_auto.jpg') or fname.endswith('_manual.jpg'):
            try:
                os.remove(os.path.join(folder, fname))
                print(f"Deleted: {fname}")
            except Exception as e:
                print(f"Error deleting {fname}: {e}")


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

    remove_all_enhanced_images()  # 🔥 Hapus file lama dulu

    enhanced_img, params_used = auto_enhance(img)
    result_filename = save_image(enhanced_img, suffix="auto")

    return {
        'filename': result_filename,
        'params_used': params_used
    }


@app.route('/manual_enhance', methods=['POST'])
def manual_enhance_route():
    data = request.json
    filename = data.get('filename')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(filepath)

    remove_all_enhanced_images()  # 🔥 Hapus file lama dulu

    # Enhancement...
    img = denoise_bilateral(img, float(data.get('sigma_space', 3)), float(data.get('sigma_color', 60)))
    img = white_balance_grayworld(img,
                                   float(data.get('r_gain', 1.0)),
                                   float(data.get('g_gain', 1.0)),
                                   float(data.get('b_gain', 1.0)))
    img = enhance_contrast_clahe(img,
                                  float(data.get('clip_limit', 2.0)),
                                  int(data.get('tile_grid', 8)))
    img = enhance_saturation(img, float(data.get('saturation', 1.1)))
    img = unsharp_masking(img,
                          radius=float(data.get('sharpen_radius', 1.0)),
                          amount=float(data.get('sharpen_amount', 100)))

    result_filename = save_image(img, suffix="manual")

    return {'filename': result_filename}


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
