// Initialize map
var map = L.map('map').setView([3.139, 101.6869], 13);

// Add tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Store markers in an object so we can reference them
var markers = {};

// Add markers for potholes
var potholeData = [
{ id: "Pothole #1", lat: 3.139, lng: 101.6869 },
{ id: "Pothole #2", lat: 3.145, lng: 101.6900 }
];

potholeData.forEach(function(p) {
var marker = L.marker([p.lat, p.lng]).addTo(map)
    .bindPopup(p.id + " - GPS (" + p.lat + ", " + p.lng + ")");
markers[p.id] = marker;
});

// Add click event for list items
document.querySelectorAll('#pothole-list li').forEach(function(item) {
    item.addEventListener('click', function() {
        var lat = parseFloat(item.getAttribute('data-lat'));
        var lng = parseFloat(item.getAttribute('data-lng'));
        var id = item.innerText.split(" - ")[0]; // Extract "Pothole #1"

        // Move map to marker
        map.setView([lat, lng], 15);

        // Open popup for this pothole
        markers[id].openPopup();
    });
});