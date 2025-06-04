document.addEventListener("DOMContentLoaded", () => {
  // Bagian Form
  const uploadForm = document.getElementById("uploadForm");
  const imageUpload = document.getElementById("imageUpload");

  // Bagian Tampilan Gambar
  const originalImage = document.getElementById("originalImage");
  const enhancedImage = document.getElementById("enhancedImage");

  // Tombol-Tombol
  const autoEnhanceBtn = document.getElementById("autoEnhanceBtn");
  const downloadBtn = document.getElementById("downloadBtn");
  const applyManualChangesBtn = document.getElementById(
    "applyManualChangesBtn"
  );

  // Kontainer dan Indikator
  const manualControlsContainer = document.getElementById(
    "manualControlsContainer"
  );
  const loadingIndicator = document.getElementById("loadingIndicator");

  // Menyimpan nama file gambar yang sedang diunggah/diproses
  let currentUploadedFilename = null;
  // Menyimpan URL gambar hasil enhancement terakhir untuk acuan kontrol manual (opsional, tergantung strategi backend)
  // let currentBaseForManualEnhancement = null; // Jika manual enhancement bertahap

  // --- Fungsi Utilitas ---
  function showLoading(isLoading) {
    loadingIndicator.style.display = isLoading ? "block" : "none";
  }

  function displayError(message) {
    // Untuk sekarang menggunakan alert, bisa diganti dengan div error yang lebih baik
    alert(`Error: ${message}`);
    console.error(message);
  }

  function updateImageDisplays(originalUrl, enhancedUrl) {
    originalImage.src = originalUrl;
    enhancedImage.src = enhancedUrl;
  }

  function updateEnhancedImageDisplay(enhancedUrl) {
    // Tambahkan parameter unik untuk cache busting, memastikan gambar baru dimuat
    enhancedImage.src = enhancedUrl + "?t=" + new Date().getTime();
    updateDownloadLink(enhancedUrl);
  }

  function updateDownloadLink(enhancedUrl) {
    if (
      enhancedUrl &&
      enhancedUrl !== "#" &&
      !enhancedUrl.startsWith("https://placehold.co")
    ) {
      downloadBtn.href = enhancedUrl;
      downloadBtn.style.display = "inline-block";
      // Coba ekstrak nama file dari URL untuk atribut download
      try {
        const url = new URL(enhancedUrl, window.location.origin);
        const pathSegments = url.pathname.split("/");
        downloadBtn.download = pathSegments[pathSegments.length - 1];
      } catch (e) {
        downloadBtn.download = "enhanced_image.png"; // Fallback
      }
    } else {
      downloadBtn.style.display = "none";
    }
  }

  function enableControlsAfterUpload() {
    autoEnhanceBtn.disabled = false;
    manualControlsContainer.style.display = "block";
  }

  function resetToInitialState() {
    originalImage.src =
      "https://placehold.co/400x300/e0e0e0/757575?text=Gambar+Asli";
    enhancedImage.src =
      "https://placehold.co/400x300/e0e0e0/757575?text=Hasil+Enhancement";
    autoEnhanceBtn.disabled = true;
    downloadBtn.style.display = "none";
    downloadBtn.href = "#";
    manualControlsContainer.style.display = "none";
    currentUploadedFilename = null;

    if (imageUpload) {
      imageUpload.value = ""; // Reset input file
      const fileLabel = imageUpload.nextElementSibling;
      if (fileLabel && fileLabel.classList.contains("custom-file-label")) {
        fileLabel.textContent = "Pilih gambar...";
      }
    }
    // Reset nilai slider ke default (jika diperlukan, tapi HTML sudah punya value default)
  }

  // --- Event Listener untuk Label Input File Kustom Bootstrap ---
  if (imageUpload) {
    imageUpload.addEventListener("change", function (e) {
      const fileName = e.target.files[0]
        ? e.target.files[0].name
        : "Pilih gambar...";
      const nextSibling = e.target.nextElementSibling;
      if (nextSibling && nextSibling.classList.contains("custom-file-label")) {
        nextSibling.textContent = fileName;
      }
    });
  }

  // --- Event Listener untuk Unggah Gambar ---
  if (uploadForm) {
    uploadForm.addEventListener("submit", async function (event) {
      event.preventDefault();
      showLoading(true);
      resetToInitialState(); // Reset state sebelum unggah baru

      const formData = new FormData(this);

      try {
        const response = await fetch("/upload", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        showLoading(false);

        if (response.ok) {
          // URL gambar asli dan URL gambar "diproses" (awalnya mungkin hanya salinan)
          updateImageDisplays(
            result.original_image_url,
            result.processed_image_url
          );
          currentUploadedFilename = result.uploaded_filename;
          // currentBaseForManualEnhancement = result.original_image_url; // Basis awal adalah gambar asli
          enableControlsAfterUpload();
          updateDownloadLink(null); // Sembunyikan tombol download sampai ada hasil enhancement nyata
        } else {
          displayError(result.error || "Gagal mengunggah gambar.");
          resetToInitialState();
        }
      } catch (error) {
        showLoading(false);
        displayError("Terjadi kesalahan jaringan atau server.");
        resetToInitialState();
        console.error("Upload error:", error);
      }
    });
  }

  // --- Event Listener untuk Tombol Enhancement Otomatis ---
  if (autoEnhanceBtn) {
    autoEnhanceBtn.addEventListener("click", async () => {
      if (!currentUploadedFilename) {
        displayError("Silakan unggah gambar terlebih dahulu.");
        return;
      }
      showLoading(true);
      try {
        const response = await fetch("/enhance_auto", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ filename: currentUploadedFilename }),
        });

        const result = await response.json();
        showLoading(false);

        if (response.ok) {
          updateEnhancedImageDisplay(result.enhanced_image_url);
          // currentBaseForManualEnhancement = result.enhanced_image_url; // Update basis untuk manual
        } else {
          displayError(result.error || "Gagal melakukan enhancement otomatis.");
        }
      } catch (error) {
        showLoading(false);
        displayError(
          "Terjadi kesalahan jaringan atau server saat enhancement otomatis."
        );
        console.error("Auto enhance error:", error);
      }
    });
  }

  // --- Event Listener untuk Slider Kontrol Manual (Memperbarui Tampilan Nilai) ---
  const sliders = [
    { id: "sigma_space", valId: "sigma_space_val" },
    { id: "sigma_color", valId: "sigma_color_val" },
    { id: "r_gain", valId: "r_gain_val" },
    { id: "g_gain", valId: "g_gain_val" },
    { id: "b_gain", valId: "b_gain_val" },
    { id: "clip_limit", valId: "clip_limit_val" },
    { id: "tile_grid_size", valId: "tile_grid_size_val" },
    { id: "saturation", valId: "saturation_val", unit: "%" },
    { id: "sharpen_radius", valId: "sharpen_radius_val", unit: " px" },
    { id: "sharpen_amount", valId: "sharpen_amount_val", unit: "%" },
  ];

  sliders.forEach((sliderConfig) => {
    const sliderElement = document.getElementById(sliderConfig.id);
    const valueDisplayElement = document.getElementById(sliderConfig.valId);
    if (sliderElement && valueDisplayElement) {
      // Set nilai awal dari value slider
      valueDisplayElement.textContent =
        sliderElement.value + (sliderConfig.unit || "");
      // Update saat slider digerakkan
      sliderElement.addEventListener("input", () => {
        valueDisplayElement.textContent =
          sliderElement.value + (sliderConfig.unit || "");
      });
    }
  });

  // --- Event Listener untuk Tombol Terapkan Perubahan Manual ---
  if (applyManualChangesBtn) {
    applyManualChangesBtn.addEventListener("click", async () => {
      if (!currentUploadedFilename) {
        displayError("Silakan unggah gambar terlebih dahulu.");
        return;
      }
      showLoading(true);

      const params = {
        filename: currentUploadedFilename, // Selalu proses dari file asli yang diunggah
        // base_image_url: currentBaseForManualEnhancement, // Atau kirim URL gambar terakhir sebagai basis
        denoise_params: {
          sigma_space: parseFloat(document.getElementById("sigma_space").value),
          sigma_color: parseFloat(document.getElementById("sigma_color").value),
        },
        white_balance_params: {
          r_gain: parseFloat(document.getElementById("r_gain").value),
          g_gain: parseFloat(document.getElementById("g_gain").value),
          b_gain: parseFloat(document.getElementById("b_gain").value),
        },
        clahe_params: {
          clip_limit: parseFloat(document.getElementById("clip_limit").value),
          tile_grid_size: parseInt(
            document.getElementById("tile_grid_size").value
          ),
        },
        saturation_params: {
          percentage: parseInt(document.getElementById("saturation").value),
        },
        sharpen_params: {
          radius: parseFloat(document.getElementById("sharpen_radius").value),
          // Amount dari slider (0-200%) perlu dikonversi di backend (misal: amount/100)
          amount: parseInt(document.getElementById("sharpen_amount").value),
        },
      };

      try {
        const response = await fetch("/enhance_manual", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(params),
        });

        const result = await response.json();
        showLoading(false);

        if (response.ok) {
          updateEnhancedImageDisplay(result.enhanced_image_url);
          // currentBaseForManualEnhancement = result.enhanced_image_url; // Update basis jika manual bertahap
        } else {
          displayError(result.error || "Gagal menerapkan perubahan manual.");
        }
      } catch (error) {
        showLoading(false);
        displayError(
          "Terjadi kesalahan jaringan atau server saat menerapkan perubahan manual."
        );
        console.error("Manual enhance error:", error);
      }
    });
  }
});
