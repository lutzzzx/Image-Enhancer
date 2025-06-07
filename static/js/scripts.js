// Ensure filename is correctly passed from Flask/Jinja2 or set to null if not available
const filename = document.body.dataset.filename || null;

// DOM Elements
const enhancedImg = document.getElementById("enhanced-img");
const enhancedImgPlaceholderText = document.getElementById(
  "enhanced-img-placeholder-text"
);
const downloadLink = document.getElementById("download-link");
const downloadHint = document.getElementById("download-hint");
const loadingIndicator = document.getElementById("loading-indicator");
const resetManualControlsButton = document.getElementById(
  "reset-manual-controls"
);

// Initial default values for sliders (matching HTML)
const defaultSliderValues = {
  sigma_space: "0",
  sigma_color: "0",
  r_gain: "1.0",
  g_gain: "1.0",
  b_gain: "1.0",
  clip_limit: "0",
  tile_grid: "1",
  saturation: "1",
  sharpen_radius: "0.1",
  sharpen_amount: "0",
};

// Function to show loading state
function showLoading() {
  if (loadingIndicator) loadingIndicator.style.display = "block";
  if (enhancedImg) enhancedImg.style.display = "none";
  if (enhancedImgPlaceholderText)
    enhancedImgPlaceholderText.textContent = "Processing...";
}

// Function to hide loading state
function hideLoading() {
  if (loadingIndicator) loadingIndicator.style.display = "none";
}

function updateSlider(id, value) {
  const slider = document.getElementById(id);
  const label = document.getElementById(`${id}_value`);
  if (slider && label) {
    slider.value = value;
    label.textContent = value;
  }
}

function autoEnhance() {
  if (!filename) {
    console.error("No filename available for auto enhancement.");
    // Optionally, display a user-friendly message here
    return;
  }
  showLoading();
  fetch("/auto_enhance", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `filename=${filename}`,
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      if (data.filename) {
        showResult(data.filename);

        // Jika ada params_used, update nilai slider/input

        if (data.params_used.sigma_space !== undefined) {
          updateSlider("sigma_space", data.params_used.sigma_space);
        }
        if (data.params_used.sigma_color !== undefined) {
          updateSlider("sigma_color", data.params_used.sigma_color);
        }
        // Update White Balance sliders
        if (data.params_used.r_gain !== undefined) {
          updateSlider("r_gain", data.params_used.r_gain.toFixed(2));
        }
        if (data.params_used.g_gain !== undefined) {
          updateSlider("g_gain", data.params_used.g_gain.toFixed(2));
        }
        if (data.params_used.b_gain !== undefined) {
          updateSlider("b_gain", data.params_used.b_gain.toFixed(2));
        }
        //Contras (CLAHE)
        if (data.params_used.clip_limit !== undefined) {
          updateSlider("clip_limit", data.params_used.clip_limit.toFixed(2));
        }
        if (data.params_used.tile_grid !== undefined) {
          updateSlider("tile_grid", data.params_used.tile_grid);
        }
        //Saturation
        if (data.params_used.saturation !== undefined) {
          updateSlider("saturation", data.params_used.saturation.toFixed(2));
        }
        // Sharpen (Unsharp Mask)
        if (data.params_used.sharpen_radius !== undefined) {
          updateSlider(
            "sharpen_radius",
            data.params_used.sharpen_radius.toFixed(2)
          );
        }
        if (data.params_used.sharpen_amount !== undefined) {
          updateSlider(
            "sharpen_amount",
            data.params_used.sharpen_amount.toFixed(0)
          );
        }
      } else {
        console.error("Auto enhance error:", data.error || "Unknown error");
        if (enhancedImgPlaceholderText)
          enhancedImgPlaceholderText.textContent = "Error enhancing image.";
      }
    })
    .catch((error) => {
      console.error("Fetch error during auto enhance:", error);
      if (enhancedImgPlaceholderText)
        enhancedImgPlaceholderText.textContent =
          "Error: Could not connect to server.";
    })
    .finally(() => {
      hideLoading();
    });
}

function manualEnhance() {
  if (!filename) {
    console.error("No filename available for manual enhancement.");
    return;
  }
  showLoading();
  const params = {
    filename,
    sigma_space: document.getElementById("sigma_space").value,
    sigma_color: document.getElementById("sigma_color").value,
    r_gain: document.getElementById("r_gain").value,
    g_gain: document.getElementById("g_gain").value,
    b_gain: document.getElementById("b_gain").value,
    clip_limit: document.getElementById("clip_limit").value,
    tile_grid: document.getElementById("tile_grid").value,
    saturation: document.getElementById("saturation").value,
    sharpen_radius: document.getElementById("sharpen_radius").value,
    sharpen_amount: document.getElementById("sharpen_amount").value,
  };

  fetch("/manual_enhance", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      if (data.filename) {
        showResult(data.filename);
      } else {
        console.error("Manual enhance error:", data.error || "Unknown error");
        if (enhancedImgPlaceholderText)
          enhancedImgPlaceholderText.textContent = "Error enhancing image.";
      }
    })
    .catch((error) => {
      console.error("Fetch error during manual enhance:", error);
      if (enhancedImgPlaceholderText)
        enhancedImgPlaceholderText.textContent =
          "Error: Could not connect to server.";
    })
    .finally(() => {
      hideLoading();
    });
}

function showResult(newFilename) {
  const path = `/static/uploads/${newFilename}?t=${new Date().getTime()}`; // Cache buster
  if (enhancedImg) {
    enhancedImg.src = path;
    enhancedImg.style.display = "block";
  }
  if (enhancedImgPlaceholderText) {
    enhancedImgPlaceholderText.style.display = "none";
  }
  if (downloadLink) {
    downloadLink.href = `/download/${newFilename}`;
    downloadLink.style.display = "inline-block";
  }
  if (downloadHint) {
    downloadHint.style.display = "none";
  }
}

// Update slider value display and add event listeners
function setupSliderListeners() {
  const sliders = [
    "sigma_space",
    "sigma_color",
    "r_gain",
    "g_gain",
    "b_gain",
    "clip_limit",
    "tile_grid",
    "saturation",
    "sharpen_radius",
    "sharpen_amount",
  ];
  sliders.forEach((id) => {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}_value`);
    if (slider && valueDisplay) {
      // Set initial display value
      valueDisplay.textContent = slider.value;
      // Update display on input
      slider.addEventListener("input", () => {
        valueDisplay.textContent = slider.value;
      });
    }
  });
}

// Reset manual controls to default values
function resetControls() {
  for (const id in defaultSliderValues) {
    const slider = document.getElementById(id);
    const valueDisplay = document.getElementById(`${id}_value`);
    if (slider) {
      slider.value = defaultSliderValues[id];
    }
    if (valueDisplay) {
      valueDisplay.textContent = defaultSliderValues[id];
    }
  }
  // Optionally, you might want to clear the enhanced image or re-apply with default settings
  // For now, it just resets the sliders.
  console.log("Manual controls reset to default values.");
}

// Set current year in footer
document.getElementById("current-year").textContent = new Date().getFullYear();

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  if (filename) {
    // Only setup sliders if an image has been uploaded
    setupSliderListeners();
    if (resetManualControlsButton) {
      resetManualControlsButton.addEventListener("click", resetControls);
    }
  }

  // If there's a filename in the URL (e.g. after upload and redirect),
  // and an enhanced image was previously generated for this session,
  // try to load it. This part is tricky without server-side session state
  // for the enhanced image name. The current `showResult` is client-side.
  // For simplicity, we'll assume the enhanced image is cleared on page load
  // unless the server specifically provides the enhanced image name.
  // The current logic only shows enhanced image after an action (auto/manual enhance).
});

// Handle image upload preview (optional, client-side only)
const imageUploadInput = document.getElementById("image-upload");
if (imageUploadInput) {
  imageUploadInput.addEventListener("change", function (event) {
    if (event.target.files && event.target.files[0]) {
      // This part is tricky because the 'original-img' is set by Flask after upload.
      // To show a client-side preview BEFORE upload, you'd need a separate img tag.
      // For now, we rely on Flask to display the original image post-upload.
      console.log("File selected:", event.target.files[0].name);
    }
  });
}
