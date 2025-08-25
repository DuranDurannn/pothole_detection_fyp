from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pathlib

from inference import run_inference

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads_video"
PREDICTION_FOLDER = "Predictions"
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

    # Run inference only on the video
    run_inference(video_path, output_dir=PREDICTION_FOLDER)

    return jsonify({
        'message': 'Upload and inference completed successfully',
        'uploaded_file': video_file.filename,
        'prediction_path': os.path.join(PREDICTION_FOLDER, "detection")
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
