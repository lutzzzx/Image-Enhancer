<div align="center">
  <a href="https://pixva.lutfinity.space/">
    <img src="https://raw.githubusercontent.com/Lutzzzx/pixva/main/static/image/pixva-logo.jpg" alt="Pixva Logo" width="150">
  </a>
  <h1>Pixva - AI Image Enhancer</h1>
  <p><strong>Revolusi AI untuk Gambar Sempurna</strong></p>
  <p>
    Aplikasi web canggih yang mentransformasi kualitas gambar Anda secara instan menggunakan analisis cerdas dan kontrol penyuntingan manual yang intuitif.
    <br><br>
    <a href="https://pixva.lutfinity.space/" target="_blank"><strong>🚀 Lihat Demo Langsung »</strong></a> ·
    <a href="#-fitur-unggulan">Fitur</a> ·
    <a href="#-instalasi--menjalankan">Instalasi</a>
  </p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/Lutzzzx/pixva/main/static/image/pixva-demo.gif" alt="Demo Pixva" width="80%">
</div>

---

## 💡 Tentang Proyek

**Pixva** adalah aplikasi web berbasis Flask dan OpenCV yang dirancang sebagai solusi lengkap peningkatan kualitas citra (_image enhancement_). Tidak seperti editor biasa, Pixva menggabungkan dua pendekatan:

1. **Peningkatan Otomatis Cerdas:** AI menganalisis aspek gambar seperti noise, kontras, warna, dan ketajaman, lalu menerapkan peningkatan adaptif.
2. **Kontrol Manual Presisi:** Tersedia panel editor dengan slider real-time untuk pengaturan detail seperti _denoise_, white balance, gamma, dan lainnya.

Antarmukanya modern, responsif, dan ramah perangkat mobile.

---

## ✨ Fitur Unggulan

| Ikon | Fitur                            | Deskripsi                                                                                       |
| :--: | -------------------------------- | ----------------------------------------------------------------------------------------------- |
|  🧠  | **Peningkatan Otomatis Cerdas**  | Analisis noise, kontras, warna, dan blur untuk menghasilkan peningkatan adaptif.                |
|  🎛️  | **Editor Manual Komprehensif**   | Kontrol real-time atas Denoise, White Balance, Gamma, Kontras (CLAHE), Saturasi, dan Ketajaman. |
|  ↔️  | **Perbandingan Real-Time**       | Tombol _toggle_ untuk melihat perbandingan gambar asli vs hasil yang telah ditingkatkan.        |
|  📂  | **Dukungan Format Luas**         | Mendukung JPG, PNG, WEBP, BMP, TIFF, hingga HEIC/HEIF.                                          |
|  📱  | **Antarmuka Modern & Responsif** | Desain dual-panel untuk desktop dan layout adaptif untuk perangkat mobile.                      |
|  🔒  | **Privasi Terjamin**             | Gambar dihapus otomatis setelah sesi berakhir, menjaga kerahasiaan pengguna.                    |

---

## 🛠️ Tumpukan Teknologi

| Kategori             | Teknologi                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend**          | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000?style=for-the-badge&logo=flask&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)                                                                                                                            |
| **Pemrosesan Citra** | ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white) ![Pillow](https://img.shields.io/badge/Pillow-306998?style=for-the-badge&logo=pillow&logoColor=white)                                                                                                                               |
| **Frontend**         | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white) |
| **Tambahan**         | `pillow-heif` untuk dukungan gambar HEIC/HEIF                                                                                                                                                                                                                                                                                                                                                                                                |

---

## 🚀 Instalasi & Menjalankan

### 1. Prasyarat

- Python 3.8 atau lebih tinggi
- `pip` dan `venv` aktif

### 2. Clone Repositori

```bash
git clone https://github.com/Lutzzzx/pixva.git
cd pixva
```

### 3. Buat dan Aktifkan Virtual Environment

> **Disarankan** menggunakan _virtual environment_ agar dependensi tidak bercampur dengan proyek lain.

- **macOS/Linux**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 4. Instal Dependensi

```bash
pip install -r requirements.txt
```

### 5. Jalankan Aplikasi

```bash
python app.py
```

Aplikasi dapat diakses melalui: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧠 Cara Kerja Algoritma Auto-Enhance

### Analisis Gambar (`utils/analysis.py`):

- **Noise:** Gaussian blur subtraction untuk estimasi deviasi standar.
- **Warna:** Deteksi color cast melalui deviasi kanal RGB.
- **Kecerahan & Kontras:** Histogram untuk deteksi rentang dinamis.
- **Ketajaman:** Varians Laplacian untuk deteksi blur.

### Peningkatan Adaptif (`utils/enhance.py`):

- **White Balance:** Koreksi berdasarkan tingkat color cast.
- **Denoising:** Pilih metode dan parameter sesuai level noise.
- **Kecerahan:** Gamma disesuaikan otomatis.
- **Kontras:** CLAHE dengan parameter adaptif.
- **Saturasi:** Peningkatan jika warna kurang hidup.
- **Penajaman:** Disesuaikan tergantung ketajaman & noise.

---

## 📁 Struktur Proyek

```
pixva/
├── app.py               # Aplikasi utama Flask
├── requirements.txt     # Daftar dependensi
├── .gitignore
│
├── utils/
│   ├── analysis.py      # Analisis gambar
│   └── enhance.py       # Proses peningkatan citra
│
├── static/
│   ├── css/style.css
│   ├── js/scripts.js
│   ├── image/
│   └── uploads/
│
└── templates/
    ├── index.html
    └── editor.html
```

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).
