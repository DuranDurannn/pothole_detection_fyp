import json
import re
import csv
import subprocess

def srt_to_csv(input_file, output_file):
    pattern_time = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")
    pattern_gps = re.compile(r"GPS \((-?\d+\.\d+),\s*(-?\d+\.\d+),\s*(-?\d+)\)")

    rows = []
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        time_match = pattern_time.search(lines[i])
        if time_match:
            time_start = time_match.group(1).replace(",", ".")
            time_end = time_match.group(2).replace(",", ".")
            gps_match = pattern_gps.search(lines[i+1])
            if gps_match:
                lon, lat, alt = gps_match.groups()
                rows.append([time_start, time_end, lon, lat, alt])

    # Write to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["time_start", "time_end", "GPS_lon", "GPS_lat", "GPS_alt"])
        writer.writerows(rows)
    
def get_video_info(mp4_file):
    try:
        # Run ffprobe to get fps and duration in JSON
        result = subprocess.run([
            "ffprobe", 
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            "-select_streams", "v:0",  # only video stream
            mp4_file
        ], capture_output=True, text=True, check=True)

        info = json.loads(result.stdout)

        # Extract fps and duration
        stream = info["streams"][0]
        fps = eval(stream["r_frame_rate"])  # convert "30/1" to number
        duration = float(stream["duration"])

        return {
            "fps": fps,
            "duration": duration
        }

    except Exception as e:
        print(f"Error probing video: {e}")
        return None

if __name__ == "__main__":
    info = get_video_info("backend/Predictions/predict/output.mp4")
    print(info)