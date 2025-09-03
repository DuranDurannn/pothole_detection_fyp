// Get the query parameter from URL
const params = new URLSearchParams(window.location.search);
const folder = params.get("detection");  // e.g. "prediction1" Folder from URL

if (folder) {
    // Update video source dynamically
    const videoSource = document.getElementById("video-source");
    videoSource.src = `../backend/Predictions/${folder}/output.mp4`;
    console.log("Video source set to:", videoSource.src);

    // Initialize Leaflet map
    const map = L.map("map").setView([0, 0], 2); // Default world view
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    let activeMarker = null; // Track the currently displayed marker

    // File source → now only merged.json
    const mergedSource = `../backend/Predictions/${folder}/merged.json`;

    fetch(mergedSource)
        .then(r => r.json())
        .then(mergedData => {
            console.log("Merged data:", mergedData);

            const listContainer = document.getElementById("detection-list");
            listContainer.innerHTML = ""; // clear placeholder list

            mergedData.forEach((entry) => {
                const { GPS_lat, GPS_lon, GPS_alt, seconds, frame, detections } = entry;

                if (!detections || detections.length === 0) return;

                detections.forEach(det => {
                    const defectName = det.name || "Unknown defect";
                    const confidence = det.confidence ? det.confidence.toFixed(2) : null;

                    const videoTime = seconds;

                    // Build popup content
                    const popupContent = `
                        <b>${defectName}</b><br>
                        Frame: ${frame}<br>
                        Time: ${videoTime.toFixed(2)}s<br>
                        Lat: ${GPS_lat}, Lon: ${GPS_lon}, Alt: ${GPS_alt}<br>
                        ${confidence ? `Confidence: ${confidence}` : ""}
                    `;

                    // Create list item
                    const li = document.createElement("li");
                    li.textContent = `${defectName} - GPS (${GPS_lat}, ${GPS_lon})`;
                    li.dataset.lat = GPS_lat;
                    li.dataset.lng = GPS_lon;
                    li.dataset.seconds = videoTime;
                    li.dataset.popup = popupContent;

                    // On click → show marker + jump to video
                    li.addEventListener("click", () => {
                        const video = document.getElementById("analysis-video");
                        video.currentTime = videoTime;
                        video.pause();

                        // Remove previous marker
                        if (activeMarker) {
                            map.removeLayer(activeMarker);
                        }

                        // Add new marker
                        activeMarker = L.marker([GPS_lat, GPS_lon]).addTo(map);
                        activeMarker.bindPopup(popupContent).openPopup();

                        // Center map on marker
                        map.setView([GPS_lat, GPS_lon], 17);
                    });

                    listContainer.appendChild(li);
                });
            });
        })
        .catch(error => console.error(error));

    // Reload video source
    const video = document.getElementById("analysis-video");
    video.load();
}
