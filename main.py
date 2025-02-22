import os
import time
from flask import Flask, send_from_directory, request, Response, render_template, stream_with_context
from app import create_app
from app.services.detection_services import detect_and_save  # Ensure this exists

app = create_app()

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_folder = os.path.join(os.getcwd(), 'assets')
    return send_from_directory(assets_folder, filename)

# ✅ SSE Route to Send Processing Updates to Frontend
@app.route('/progress')
def progress():
    def generate():
        for i in range(1, 101, 10):  # Simulate 10% progress steps
            time.sleep(1)  # Simulate work being done
            yield f"data: Processing detections: {i}% complete\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

# ✅ Image Upload Route (Triggers Processing)
@app.route('/upload', methods=['POST'])
def upload_image():
    if "image" not in request.files:
        return "No image file provided", 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return "No selected file", 400

    # Save file to uploads
    upload_path = os.path.join(os.getcwd(), "uploads", image_file.filename)
    image_file.save(upload_path)

    # Run detection
    detect_and_save(upload_path)

    return "Processing complete!", 200

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=8080, debug=True)