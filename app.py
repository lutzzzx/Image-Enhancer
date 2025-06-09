from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import uuid
import numpy as np
import pillow_heif
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

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 🔒 Batas upload 10 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_WIDTH = 1920
MAX_HEIGHT = 1080

def convert_heic_to_jpg(file_path, save_folder):
    """Konversi HEIC ke JPG dengan resize menggunakan pillow-heif"""
    heif_file = pillow_heif.read_heif(file_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data
    )
    image = resize_image(image)
    new_filename = f"{uuid.uuid4().hex}_original.jpg"
    new_path = os.path.join(save_folder, new_filename)
    image.save(new_path, "JPEG", quality=85)
    return new_filename


def resize_image(image):
    """Resize gambar jika terlalu besar"""
    width, height = image.size
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        ratio = min(MAX_WIDTH / width, MAX_HEIGHT / height)
        new_size = (int(width * ratio), int(height * ratio))
        return image.resize(new_size, Image.LANCZOS)
    return image

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
            except Exception as e:
                print(f"Error deleting {fname}: {e}")

def allowed_file(filename):
    """Validasi ekstensi file"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.heif', '.heic']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return (
                "Unsupported file format. Please upload an image with one of these extensions: "
                ".jpg, .jpeg, .png, .bmp, .tiff, .tif, .webp, .heif, .heic."
            ), 400

        ext = os.path.splitext(file.filename)[1].lower()
        try:
            if ext == '.heic':
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}_temp.heic")
                file.save(temp_path)
                filename = convert_heic_to_jpg(temp_path, app.config['UPLOAD_FOLDER'])
                os.remove(temp_path)
            else:
                image = Image.open(file.stream)
                image = resize_image(image)
                filename = f"{uuid.uuid4().hex}_original.jpg"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath, "JPEG", quality=85)
        except Exception as e:
            print(f"Error processing image: {e}")
            return "Error processing image.", 500

        return render_template('index.html', filename=filename)

    return render_template('index.html', filename=None)

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return "Unsupported file format. Please upload JPG, PNG, or HEIC.", 400

        ext = os.path.splitext(file.filename)[1].lower()
        try:
            if ext == '.heic':
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}_temp.heic")
                file.save(temp_path)
                filename = convert_heic_to_jpg(temp_path, app.config['UPLOAD_FOLDER'])
                os.remove(temp_path)
            else:
                image = Image.open(file.stream)
                image = resize_image(image)
                filename = f"{uuid.uuid4().hex}_original.jpg"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath, "JPEG", quality=85)
        except Exception as e:
            print(f"Error processing image: {e}")
            return "Error processing image.", 500

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
