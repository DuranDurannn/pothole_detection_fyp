import csv
import json

# Input and output file paths
csv_file = "backend/Predictions/predict/geo.csv"   # your CSV file
json_file = "backend/Predictions/predict/geo.json" # output JSON file

# Read CSV and convert to list of dicts
data = []
with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convert numeric values (longitude, latitude, altitude) to float/int
        row["GPS_lon"] = float(row["GPS_lon"])
        row["GPS_lat"] = float(row["GPS_lat"])
        row["GPS_alt"] = int(row["GPS_alt"])
        data.append(row)

# Write to JSON
with open(json_file, mode="w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✅ Converted {csv_file} to {json_file}")