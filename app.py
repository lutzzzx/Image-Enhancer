from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import uuid
import numpy as np
import pyheif
from PIL import Image

# Import fungsi enhancement
from utils.enhance import (
    auto_enhance,
    denoise_bilateral,
    white_balance_grayworld,
    enhance_contrast_clahe,
    enhance_saturation,
    unsharp_masking,
    gamma_correction
)

# Inisialisasi Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload tersedia
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def convert_heic_to_jpg(file_path, save_folder):
    """Konversi file HEIC ke JPG"""
    heif_file = pyheif.read(file_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    new_filename = f"{uuid.uuid4().hex}_original.jpg"
    new_path = os.path.join(save_folder, new_filename)
    image.save(new_path, "JPEG")
    return new_filename

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

        ext = os.path.splitext(file.filename)[1].lower()
        if ext == '.heic':
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}_temp.heic")
            file.save(temp_path)
            filename = convert_heic_to_jpg(temp_path, app.config['UPLOAD_FOLDER'])
            os.remove(temp_path)
        else:
            filename = f"{uuid.uuid4().hex}_original.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        return render_template('index.html', filename=filename)

    return render_template('index.html', filename=None)

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)

        ext = os.path.splitext(file.filename)[1].lower()
        if ext == '.heic':
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}_temp.heic")
            file.save(temp_path)
            filename = convert_heic_to_jpg(temp_path, app.config['UPLOAD_FOLDER'])
            os.remove(temp_path)
        else:
            filename = f"{uuid.uuid4().hex}_original.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

        return render_template('editor.html', filename=filename)

    return render_template('editor.html', filename=None)

@app.route('/auto_enhance', methods=['POST'])
def auto_enhance_route():
    filename = request.form.get('filename')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(filepath)

    if img is None:
        return {'error': 'Gambar tidak dapat dibaca. Pastikan format file didukung.'}, 400

    remove_all_enhanced_images()

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

    if img is None:
        return {'error': 'Gambar tidak dapat dibaca. Pastikan format file didukung.'}, 400

    remove_all_enhanced_images()

    # Manual enhancement
    img = white_balance_grayworld(img,
                                  float(data.get('r_gain', 1.0)),
                                  float(data.get('g_gain', 1.0)),
                                  float(data.get('b_gain', 1.0)))
    img = denoise_bilateral(img, float(data.get('sigma_space', 3)), float(data.get('sigma_color', 60)))
    img = gamma_correction(img, float(data.get('gamma', 1.0)))
    img = enhance_contrast_clahe(img,
                                  float(data.get('clip_limit', 2.0)),
                                  int(data.get('tile_grid', 8)))
    img = enhance_saturation(img, float(data.get('saturation', 1.0)))
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
