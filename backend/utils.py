from collections import Counter
import datetime
import json
import os
import re
import csv
import subprocess

def parse_time_to_seconds(time_str):
    # Example format: "00:00:00.033"
    t = datetime.datetime.strptime(time_str, "%H:%M:%S.%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6

def srt_to_json(input_file, output_file):
    pattern_time = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")
    pattern_gps = re.compile(r"\[latitude:\s*(-?\d+\.\d+)\]\s*\[longitude:\s*(-?\d+\.\d+)\]\s*\[rel_alt:\s*(-?\d+\.\d+)")
    pattern_frame = re.compile(r"FrameCnt:\s*(\d+)")

    data = []
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        time_match = pattern_time.search(lines[i])
        if time_match:
            time_start = time_match.group(1).replace(",", ".")
            time_end = time_match.group(2).replace(",", ".")

            # look for frame info and GPS in following lines
            frame_match = None
            gps_match = None
            for j in range(1, 4):  # check up to 3 lines ahead
                if i + j < len(lines):
                    if not frame_match:
                        frame_match = pattern_frame.search(lines[i+j])
                    if not gps_match:
                        gps_match = pattern_gps.search(lines[i+j])

            if gps_match and frame_match:
                lat, lon, alt = gps_match.groups()
                frame = int(frame_match.group(1))

                entry = {
                    "frame": frame,
                    "time_start": time_start,
                    "time_end": time_end,
                    "GPS_lon": float(lon),
                    "GPS_lat": float(lat),
                    "GPS_alt": float(alt),
                    "seconds": parse_time_to_seconds(time_start)
                }
                data.append(entry)

    # Save as JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Converted {input_file} → {output_file} ({len(data)} records)")
    
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

def convert_with_original(video_file, original_video, output_file):
     # Get original video duration
    original_video = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", original_video],
        capture_output=True, text=True
    )
    original_video_duration = float(original_video.stdout.strip())

     # Get detected video duration
    result_video = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_file],
        capture_output=True, text=True
    )
    result_video_duration = float(result_video.stdout.strip())

    # Compute scale factor
    scale = original_video_duration / result_video_duration

    subprocess.run([
        "ffmpeg", "-y", "-i", video_file,
        "-filter:v", f"setpts={scale}*PTS",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_file
    ], check=True)

    if os.path.exists(video_file):
        os.remove(video_file)
        print(f"Deleted {video_file}")

    print(f"Converted {video_file} to {output_file} with scale={scale:.6f}")

def geo_detection_merger(geo_file, best_detections_file, output_file):
    # Load both JSON files
    with open(geo_file) as f:
        geo_data = json.load(f)

    with open(best_detections_file) as f:
        detections_data = json.load(f)

    # Build a lookup: frame → detections
    frame_lookup = {}
    for det_group in detections_data:
        for det in det_group.get("best_detections", []):
            frame = det.get("frame")
            if frame is not None:
                frame_lookup.setdefault(frame, []).append(det)

    # Merge by matching frame
    merged = []
    for entry in geo_data:
        frame = entry.get("frame")
        if frame is not None:
            entry["detections"] = frame_lookup.get(frame, [])  # match by frame
            merged.append(entry)

    # Save merged JSON
    with open(os.path.join(output_file), "w") as f:
        json.dump(merged, f, indent=2)

def get_count(detection_file, output_file):
    # Load JSON
    with open(detection_file, "r") as f:
        data = json.load(f)

    # Count detections
    counter = Counter()
    for sec_data in data:
        for det in sec_data["best_detections"]:
            counter[det["name"]] += 1