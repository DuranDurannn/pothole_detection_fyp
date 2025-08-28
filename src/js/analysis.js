// Get the query parameter from URL
const params = new URLSearchParams(window.location.search);
const folder = params.get("detection");  // e.g. "prediction1" Folder from URL

if (folder) {
    // Update video source dynamically
    const videoSource = document.getElementById("video-source");
    videoSource.src = `../backend/Predictions/${folder}/output.mp4`;
    console.log("Video source set to:", videoSource.src);

    // Update geo info source
    const geoSource = `../backend/Predictions/${folder}/geo.json`;
    fetch(geoSource)
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to load geo.json");
            }
            return response.json();
        })
        .then(data => {
            console.log("GeoJSON data:", data);

            // Example: show it on the page
            const geoContainer = document.getElementById("geo-container");
            geoContainer.textContent = JSON.stringify(data, null, 2);

            // Or: pass it to Leaflet/Mapbox/etc. if you want to render it on a map
        })
        .catch(error => console.error(error));

    // !PUT LOAD AT THE END OR ELSE IT WONT LOAD LOL 
    const video = document.getElementById("analysis-video");
    video.load(); // reload the video with new source
}