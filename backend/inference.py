from ultralytics import YOLO
import os

# Load YOLO model once
model = YOLO("backend/Model/best.pt")

def run_inference(video_path, output_dir="backend/Predictions"):
    """
    Run YOLO inference on uploaded video and save results.
    Save results.txt in the same folder as the output video.
    """
    results = model.predict(
        source=video_path,
        imgsz=1920,
        device=0,
        save=True,
        project=output_dir,
        stream=True,
        name="predict",
        conf=0.3,
        iou=0.35
    )

    frame_id = 0
    save_dir = None
    output_txt = None

    for i, result in enumerate(results):
        if i == 0:  # first frame → get save_dir here
            save_dir = result.save_dir
            output_txt = os.path.join(save_dir, "results.txt")
            f = open(output_txt, "w")  # open file once

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
    return save_dir
