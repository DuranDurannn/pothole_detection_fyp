const uploadAreaVideo = document.getElementById("uploadAreaVideo");
const uploadAreaSRT = document.getElementById("uploadAreaSRT");
const fileInputVideo = document.getElementById("fileInputVideo");
const fileInputSRT = document.getElementById("fileInputSRT");
const confirmUploadBtn = document.getElementById("confirmUpload");
const clearVideoBtn = document.getElementById("clearVideo");
const clearSRTBtn = document.getElementById("clearSRT");

let videoFile = null;
let srtFile = null;

/* DRAG & DROP HELPERS */
function setupDragAndDrop(area, handler) {
  area.addEventListener("dragover", (e) => {
    e.preventDefault();
    area.classList.add("dragover");
  });

  area.addEventListener("dragleave", () => {
    area.classList.remove("dragover");
  });

  area.addEventListener("drop", (e) => {
    e.preventDefault();
    area.classList.remove("dragover");
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handler(files[0]);
    }
  });
}

/* VIDEO HANDLING */
function handleVideo(file) {
  if (!file.type.startsWith("video/")) {
    uploadAreaVideo.innerHTML = `<p style="color:red;">Unsupported file type: ${file.type}</p>`;
    return;
  }
  videoFile = file;
  uploadAreaVideo.innerHTML = "";
  const video = document.createElement("video");
  video.src = URL.createObjectURL(file);
  video.controls = true;
  video.style.maxWidth = "100%";
  video.style.maxHeight = "300px";
  video.style.borderRadius = "10px";
  uploadAreaVideo.appendChild(video);
}

fileInputVideo.addEventListener("change", () => {
  if (fileInputVideo.files.length > 0) {
    handleVideo(fileInputVideo.files[0]);
  }
});

setupDragAndDrop(uploadAreaVideo, handleVideo);

clearVideoBtn.addEventListener("click", () => {
  videoFile = null;
  uploadAreaVideo.innerHTML = "Drag to upload video";
});

/* SRT HANDLING */
function handleSRT(file) {
  if (!(file.name.endsWith(".srt") || file.name.endsWith(".txt"))) {
    uploadAreaSRT.innerHTML = `<p style="color:red;">Unsupported file type: ${file.type}</p>`;
    return;
  }
  srtFile = file;
  uploadAreaSRT.innerHTML = `<p style="color:green;">${file.name} selected</p>`;
}

fileInputSRT.addEventListener("change", () => {
  if (fileInputSRT.files.length > 0) {
    handleSRT(fileInputSRT.files[0]);
  }
});

setupDragAndDrop(uploadAreaSRT, handleSRT);

clearSRTBtn.addEventListener("click", () => {
  srtFile = null;
  uploadAreaSRT.innerHTML = "Drag to upload SRT file";
});

/* CONFIRM UPLOAD */
confirmUploadBtn.addEventListener("click", () => {
  if (!videoFile || !srtFile) {
    alert("Please upload both a video and an SRT file!");
    return;
  }

  const formData = new FormData();
  formData.append("video", videoFile);
  formData.append("srt", srtFile);

  fetch("http://127.0.0.1:5000/upload", {
    method: "POST",
    body: formData
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Response:", data);
      alert(data.message || "Upload completed!");
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Upload failed!");
    });
});
