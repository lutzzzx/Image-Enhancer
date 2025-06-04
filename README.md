# 🖼️ Image Enhancement Web App (Flask + OpenCV)

Aplikasi web interaktif untuk **peningkatan kualitas citra (image enhancement)** secara **otomatis berbasis deteksi karakteristik gambar** dan **manual melalui kontrol parameter real-time**. Dibangun dengan **Flask**, **OpenCV**, dan **JavaScript**.

---

## 🔧 Fitur Utama

### ✅ Upload Gambar

- Dukungan format `.jpg`, `.jpeg`, `.png`
- Gambar disimpan dalam folder `static/uploads`

### ✅ Enhancement Otomatis (berbasis analisis)

Proses bertahap dan adaptif:

1. **Denoising**
   - Deteksi noise (varian intensitas area datar)
   - Bilateral filter (`σ_space ≈ 3`, `σ_color ≈ 2×σ_noise`)
   - Non-Local Means untuk noise berat
2. **White Balance**
   - Gray-World Assumption
   - Deteksi color cast dari selisih kanal RGB
3. **Kontras**
   - CLAHE (`clipLimit=2.0`, `tileGridSize=(8,8)`)
   - Alternatif: histogram equalization
4. **Saturasi**
   - Tambahan 10–20% jika nilai saturasi rendah
5. **Sharpening**
   - Unsharp Masking (`radius=0.5–2 px`, `amount=50–150%`)
   - Berdasarkan varians Laplacian (blur detection)

### ✅ Enhancement Manual (Editor Real-Time)

- Kontrol parameter melalui slider:
  - `σ_space`, `σ_color` (denoising)
  - RGB gain (white balance)
  - `clipLimit`, `tileGridSize` (CLAHE)
  - Saturasi (%)
  - Sharpening `radius`, `amount`
- Preview langsung & pengunduhan hasil

### ✅ Download Gambar

- Hasil disimpan dan dapat diunduh via tombol "Download"

---

## 📁 Struktur Proyek

```

project/
│
├── app.py # Main Flask app
├── utils/
│ ├── enhance.py # Proses otomatis & manual
│ └── analysis.py # Analisis karakteristik gambar
│
├── static/
│ ├── uploads/ # Gambar original & hasil
│ └── js/
│ └── sliders.js # JS slider control
│
├── templates/
│ └── index.html # Antarmuka HTML utama
│
├── README.md

```

---

## 🚀 Instalasi & Menjalankan

### 1. Clone Repositori

```bash
git clone https://github.com/namauser/image-enhancement-app.git
cd image-enhancement-app
```

### 2. Install Dependencies

Disarankan membuat virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Isi `requirements.txt`:**

```txt
flask
opencv-python
numpy
```

### 3. Jalankan Aplikasi

```bash
python app.py
```

Akses di browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧠 Catatan Teknis

- Gambar diproses di server lokal (Flask)
- Real-time slider pakai fetch API (tanpa reload)
- Enhancement otomatis **skip** tahapan yang tidak perlu berdasarkan:

  - Varian noise
  - Histogram kontras
  - Laplacian blur detection
  - Saturation metric

- Manual override tetap memungkinkan user kontrol penuh

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah MIT License.
