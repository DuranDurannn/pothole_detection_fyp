from ultralytics import YOLO
import os
import cv2
import subprocess

from utils import srt_to_csv

# Load YOLO model once
model = YOLO("backend/Model/best.pt")

def run_inference(video_path, output_dir):
    """
    Run YOLO inference on uploaded video and save results.
    Save results.txt in the same folder as the output video.
    Convert YOLO's AVI output to MP4 for web compatibility.
    """
    results = model.predict(
        source=video_path,
        imgsz=1920,
        device=0,
        save=True,
        project=output_dir,
        name="predict",
        conf=0.3,
        iou=0.35
    )

    frame_id = 0
    save_dir = None
    output_txt = None
    avi_file = None
    mp4_file = None

    for i, result in enumerate(results):
        if i == 0:  # first frame → get save_dir here
            save_dir = result.save_dir
            output_txt = os.path.join(save_dir, "results.txt")
            f = open(output_txt, "w")  # open file once

            # YOLO saves AVI in save_dir with same name as input
            for file in os.listdir(save_dir):
                if file.endswith(".avi"):
                    avi_file = os.path.join(save_dir, file)
                    # Force final filename to "output.mp4"
                    mp4_file = os.path.join(save_dir, "output.mp4")

        frame_id += 1
        boxes = result.boxes

        f.write(f"Frame {frame_id}:\n")
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            f.write(f"  class={cls_id}, conf={conf:.2f}, bbox={xyxy}\n")
        f.write("\n")

    f.close()

    # Convert AVI → MP4 using ffmpeg
    if avi_file and mp4_file:
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", avi_file,
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

    return save_dir
