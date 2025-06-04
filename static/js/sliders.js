document.addEventListener("DOMContentLoaded", function () {
  const filename = document.body.getAttribute("data-filename");

  document.getElementById("btn-auto").addEventListener("click", () => {
    fetch("/auto_enhance", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `filename=${filename}`,
    })
      .then((res) => res.json())
      .then((data) => updateResult(data.filename));
  });

  document.getElementById("btn-manual").addEventListener("click", () => {
    const get = (id) => document.getElementById(id).value;
    const params = {
      filename,
      sigma_space: get("sigma_space"),
      sigma_color: get("sigma_color"),
      r_gain: get("r_gain"),
      g_gain: get("g_gain"),
      b_gain: get("b_gain"),
      clip_limit: get("clip_limit"),
      tile_grid: get("tile_grid"),
      saturation: get("saturation"),
      sharpen_radius: get("sharpen_radius"),
      sharpen_amount: get("sharpen_amount"),
    };

    fetch("/manual_enhance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    })
      .then((res) => res.json())
      .then((data) => updateResult(data.filename));
  });

  function updateResult(fname) {
    const imgPath = `/static/uploads/${fname}`;
    document.getElementById("enhanced-img").src = imgPath;
    const downloadLink = document.getElementById("download-link");
    downloadLink.href = `/download/${fname}`;
    downloadLink.style.display = "inline-block";
  }
});
