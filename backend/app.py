from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pathlib

from inference import run_inference, best_detections_by_second
from utils import srt_to_csv, csv_to_json, convert_with_original, geo_detection_merger

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads_video"
PREDICTION_FOLDER = "backend/Predictions"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_and_infer():
    if 'video' not in request.files or 'srt' not in request.files:
        return jsonify({'error': 'Both video and SRT files are required!'}), 400

    video_file = request.files['video']
    srt_file = request.files['srt']

    # Create a folder named after the video (without extension)
    video_stem = pathlib.Path(video_file.filename).stem
    upload_subfolder = os.path.join(UPLOAD_FOLDER, video_stem)
    os.makedirs(upload_subfolder, exist_ok=True)

    # Save video with original filename
    video_path = os.path.join(upload_subfolder, video_file.filename)
    video_file.save(video_path)

    # Force SRT name to match video stem
    srt_filename = f"{video_stem}.srt"
    srt_path = os.path.join(upload_subfolder, srt_filename)
    srt_file.save(srt_path)

    # Run detection
    file_dir, avi_dir = run_inference(video_path, output_dir=PREDICTION_FOLDER)
    print("THE AVI", avi_dir)

    # File conversion from srt to csv to json
    srt_to_csv(input_file=srt_path, output_file=os.path.join(file_dir, "geo.csv"))
    print("SRT to CSV conversion completed.")

    csv_to_json(input_file=os.path.join(file_dir, "geo.csv"),
                output_file=os.path.join(file_dir, "geo.json"))
    print("CSV to JSON conversion completed.")

    best_detections_by_second(video_path, os.path.join(file_dir, "results.json"),
                                output_file=os.path.join(file_dir, "best_detections.json"))
    
    # Convert AVI → MP4 using ffmpeg
    convert_with_original(avi_dir, os.path.normpath(video_path), os.path.join(file_dir, "output.mp4"))

    geo_detection_merger(geo_file=os.path.join(file_dir, "geo.json"),
                         best_detections_file=os.path.join(file_dir, "best_detections.json"),
                         output_file=os.path.join(file_dir, "merged.json"))

    return jsonify({
        'message': 'Upload and inference completed successfully',
        'uploaded_file': video_file.filename,
        'prediction_path': os.path.join(PREDICTION_FOLDER, "detection")
    }), 200

@app.route("/detections")
def detections():
    base_folder = "backend/Predictions"
    # Get only folders inside Predictions
    folders = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
    return jsonify({"detections": folders})

if __name__ == "__main__":
    app.run(debug=True)
