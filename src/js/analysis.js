// Initialization
const params = new URLSearchParams(window.location.search);
const folder = params.get("detection"); // e.g. "prediction1"

// Global state
window.mapInstance = null;
window.activeMarker = null;
let polyline = null;
let startMarker = null;
let endMarker = null;

// Custom icons
const greenIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const redIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


if (folder) {
  document.querySelector("h1").textContent = folder;

  // Video setup with cache-busting
  const videoSource = document.getElementById("video-source");
  videoSource.src = `../backend/Predictions/${folder}/output.mp4?t=${Date.now()}`;
  console.log("Video source set to:", videoSource.src);

  const video = document.getElementById("analysis-video");
  video.load();

  // Map setup
  window.mapInstance = L.map("map").setView([0, 0], 2);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(window.mapInstance);

  // Fetch merged.json with cache-busting
  const mergedSource = `../backend/Predictions/${folder}/merged.json?t=${Date.now()}`;

  fetch(mergedSource)
    .then(r => r.json())
    .then(mergedData => {
      console.log("Merged data (fresh):", mergedData);

      const listContainer = document.getElementById("detection-list");
      listContainer.innerHTML = "";

      const detectionCounts = {};
      const flightPath = [];

      // Process detections
      mergedData.forEach((entry) => {
        const { GPS_lat, GPS_lon, GPS_alt, seconds, frame, detections } = entry;

        // Collect flight path
        if (GPS_lat && GPS_lon) {
          flightPath.push([GPS_lat, GPS_lon]);
        }

        if (!detections || detections.length === 0) return;

        detections.forEach(det => {
          const defectName = det.name || "Unknown defect";
          detectionCounts[defectName] = (detectionCounts[defectName] || 0) + 1;

          const videoTime = seconds;

          const popupContent = `
            <b>${defectName}</b><br>
            Frame: ${frame}<br>
            Time: ${videoTime.toFixed(2)}s<br>
            Lat: ${GPS_lat}, Lon: ${GPS_lon}, Alt: ${GPS_alt}<br>
          `;

          const li = document.createElement("li");
          li.textContent = `${defectName} - GPS (${GPS_lat}, ${GPS_lon})`;
          li.dataset.lat = GPS_lat;
          li.dataset.lng = GPS_lon;
          li.dataset.seconds = videoTime;
          li.dataset.popup = popupContent;

          // On click → jump to video + show marker
          li.addEventListener("click", () => {
            video.currentTime = videoTime;
            video.pause();

            if (window.activeMarker) {
              window.mapInstance.removeLayer(window.activeMarker);
            }

            window.activeMarker = L.marker([GPS_lat, GPS_lon]).addTo(window.mapInstance);
            window.activeMarker.bindPopup(popupContent);

            window.mapInstance.setView([GPS_lat, GPS_lon], 20);
            setTimeout(() => window.activeMarker.openPopup(), 200);
          });

          listContainer.appendChild(li);
        });
      });

      // Draw flight path
      if (flightPath.length > 1) {
        polyline = L.polyline(flightPath, { color: "red", weight: 3 });
        polyline.addTo(window.mapInstance);
        window.mapInstance.fitBounds(polyline.getBounds());
      }

      // Start & End markers
      if (flightPath.length > 1) {
        const startCoords = flightPath[0];
        const endCoords = flightPath[flightPath.length - 1];

        startMarker = L.marker(startCoords, { icon: greenIcon, title: "Start" })
          .bindPopup("<b>Start of Flight</b>")
          .addTo(window.mapInstance);

        endMarker = L.marker(endCoords, { icon: redIcon, title: "End" })
          .bindPopup("<b>End of Flight</b>")
          .addTo(window.mapInstance);
      }

      // Toggle switch for path
      const togglePath = document.getElementById("toggle-path");
      togglePath.addEventListener("change", () => {
        if (togglePath.checked) {
          if (polyline && !window.mapInstance.hasLayer(polyline)) {
            polyline.addTo(window.mapInstance);
          }
        } else {
          if (polyline && window.mapInstance.hasLayer(polyline)) {
            window.mapInstance.removeLayer(polyline);
          }
        }
      });

      // Draw chart
      const ctx = document.getElementById("detectionChart").getContext("2d");
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: Object.keys(detectionCounts),
          datasets: [{
            label: "Detections",
            data: Object.values(detectionCounts),
            backgroundColor: [
              "rgba(255, 99, 132, 0.6)",
              "rgba(54, 162, 235, 0.6)",
              "rgba(255, 206, 86, 0.6)",
              "rgba(75, 192, 192, 0.6)",
              "rgba(153, 102, 255, 0.6)"
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
      });
    })
    .catch(error => console.error(error));
}

// Tab handling
document.addEventListener("DOMContentLoaded", () => {
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabButtons.forEach(button => {
    button.addEventListener("click", () => {
      tabButtons.forEach(btn => btn.classList.remove("active"));
      tabPanels.forEach(panel => panel.classList.remove("active"));

      button.classList.add("active");
      const targetPanel = document.getElementById(button.dataset.target + "-tab");
      targetPanel.classList.add("active");

      // Special cases for map and video
      if (button.dataset.target === "map" && window.mapInstance) {
        setTimeout(() => {
          window.mapInstance.invalidateSize();
          if (window.activeMarker) window.activeMarker.openPopup();
        }, 200);
      }

      if (button.dataset.target === "video" && window.activeMarker) {
        window.activeMarker.closePopup();
      }
    });
  });
});

const toggleStartEnd = document.getElementById("toggle-startend");
toggleStartEnd.addEventListener("change", () => {
  if (toggleStartEnd.checked) {
    if (startMarker && !window.mapInstance.hasLayer(startMarker)) {
      startMarker.addTo(window.mapInstance);
    }
    if (endMarker && !window.mapInstance.hasLayer(endMarker)) {
      endMarker.addTo(window.mapInstance);
    }
  } else {
    if (startMarker && window.mapInstance.hasLayer(startMarker)) {
      window.mapInstance.removeLayer(startMarker);
    }
    if (endMarker && window.mapInstance.hasLayer(endMarker)) {
      window.mapInstance.removeLayer(endMarker);
    }
  }
});