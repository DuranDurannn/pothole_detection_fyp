const videoInput = document.getElementById("videoFile");
const srtInput = document.getElementById("srtFile");
const uploadBtn = document.getElementById("uploadBtn");
const clearBtn = document.getElementById("clearUpload");
const statusDiv = document.getElementById("status");

let selectedVideo = null;
let selectedSrt = null;

// File selection
videoInput.addEventListener("change", () => {
  const file = videoInput.files[0];
  if (file && !file.name.toLowerCase().endsWith(".mp4")) {
    statusDiv.textContent = "Wrong type of file. Please select an MP4 video.";
    videoInput.value = "";
    selectedVideo = null;
  } else {
    selectedVideo = file;
    updateStatus();
  }
});

srtInput.addEventListener("change", () => {
  const file = srtInput.files[0];
  if (file && !file.name.toLowerCase().endsWith(".srt")) {
    statusDiv.textContent = "Wrong type of file. Please select an SRT file.";
    srtInput.value = "";
    selectedSrt = null;
  } else {
    selectedSrt = file;
    updateStatus();
  }
});

function updateStatus() {
  let msg = "";
  if (selectedVideo) msg += `${selectedVideo.name}`;
  if (selectedSrt) msg += ` | ${selectedSrt.name}`;
  statusDiv.textContent = msg || "No files selected.";
}

// Upload button
uploadBtn.addEventListener("click", async (e) => {
  e.preventDefault(); // prevent page refresh

  if (!selectedVideo || !selectedSrt) {
    statusDiv.textContent = "Please select both a video and an SRT file.";
    return;
  }

  const formData = new FormData();
  formData.append("video", selectedVideo);
  formData.append("srt", selectedSrt);

  statusDiv.textContent = "Uploading...";

  try {
    const response = await fetch("http://localhost:5000/upload", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      statusDiv.textContent = result.message || "Upload successful!";
      console.log("ID", result.detectionId);
      // Redirect to analysis page after 3s
      setTimeout(() => {
        window.location.href = "analysis.html?detection=" + result.detectionId;
      }, 3000);
    } else {
      statusDiv.textContent = `Upload failed: ${result.error || response.statusText}`;
      alert(`Upload failed: ${result.error || response.statusText}`);
    }

  } catch (error) {
    console.error(error);
    statusDiv.textContent = "Error uploading files. Check server.";
    alert("Error uploading files. Check server.");
  }
});

// Clear button
clearBtn.addEventListener("click", () => {
  selectedVideo = null;
  selectedSrt = null;
  videoInput.value = "";
  srtInput.value = "";
  updateStatus();
});
