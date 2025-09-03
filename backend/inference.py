from flask import json
from sklearn.base import defaultdict
from ultralytics import YOLO
import os
import math
import subprocess

from utils import get_video_info

# Load YOLO model once
model = YOLO("backend/Model/yolov11s_720.pt")

def run_inference(video_path, output_dir):
    """
    Run YOLO inference on uploaded video and save results.
    Save results.json in the same folder as the output video.
    Convert YOLO's AVI output to MP4 for web compatibility.
    """
    results = model.predict(
        source=video_path,
        imgsz=1920,
        device=0,
        save=True,
        stream=True,
        project=output_dir,
        name="predict",
        conf=0.45,
        iou=0.35
    )

    CLASS_NAMES = [
        "transverse_crack",
        "alligator_crack",
        "longitudinal_crack",
        "oblique_crack",
        "pothole",
        "repair"
    ]

    frame_id = 0
    save_dir = None
    avi_file = None
    mp4_file = None
    all_results = []  # collect detections

    for i, result in enumerate(results):
        if i == 0:  # first frame → get save_dir here
            save_dir = result.save_dir

            # YOLO saves AVI in save_dir with same name as input
            for file in os.listdir(save_dir):
                if file.endswith(".avi"):
                    avi_file = os.path.join(save_dir, file)
                    # Force final filename to "output.mp4"
                    mp4_file = os.path.join(save_dir, "output.mp4")

        frame_id += 1
        frame_data = {"frame": frame_id, "detections": []}

        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            frame_data["detections"].append({
                "class": cls_id,
                "name": CLASS_NAMES[cls_id],
                "confidence": conf,
                "bbox": xyxy
            })

        all_results.append(frame_data)

    # Save JSON once after loop
    if save_dir:
        output_json = os.path.join(save_dir, "results.json")
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=4, sort_keys=False)
        print(f"Results saved to {output_json}")

    """
    if avi_file and mp4_file:
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", avi_file,
                "-filter:v", "setpts=0.967*PTS",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                mp4_file
            ], check=True)
            print(f"Converted to {mp4_file}")

            if os.path.exists(avi_file):
                os.remove(avi_file)
                print(f"Deleted {avi_file}")
        except Exception as e:
            print(f"Error converting to mp4: {e}")
    """

    return save_dir, avi_file

def best_detections_by_second(video_file, result_file, output_file):
    video_info = get_video_info(video_file)
    fps = video_info["fps"]  # keep float
    duration = video_info["duration"]

    with open(result_file, "r") as f:
        data = json.load(f)

    grouped = defaultdict(list)
    for frame in data:
        frame_idx = frame["frame"]
        time_sec = int(frame_idx / fps)  # floor to nearest second
        grouped[time_sec].append(frame)

    results = []
    for sec, frames in grouped.items():
        best_by_class = {}
        for frame in frames:
            frame_idx = frame["frame"]
            frame_time = frame_idx / fps
            for det in frame["detections"]:
                cls = det["class"]
                conf = det["confidence"]
                if cls not in best_by_class or conf > best_by_class[cls]["confidence"]:
                    best_by_class[cls] = {
                        **det,
                        "frame": frame_idx,
                        "time_seconds": round(frame_time, 2)
                    }

        # Only append if it is not empty
        if best_by_class:
            results.append({
                "second": sec,
                "best_detections": list(best_by_class.values())
            })

    # Save to JSON
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)
