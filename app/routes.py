from flask import Blueprint, request, jsonify, send_from_directory, render_template, send_file
from werkzeug.utils import secure_filename
import os
import time
from app.services.detection_services import detect_and_save
from app.services.grouping_services import group_and_save
from app.utils.file_handler import save_uploaded_file
from app.utils.constants import UPLOADS_FOLDER, RESULTS_FOLDER

# Define a Blueprint for routes
routes = Blueprint("routes", __name__)

@routes.route("/", methods=["GET"])
def home():
    """
    Serve the HTML welcome page at the root endpoint.
    """
    return render_template("index.html")

@routes.route("/upload", methods=["POST"])
def upload_image():
    """
    Handle image uploads, perform detection and grouping, and return results.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    # Save uploaded file
    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = secure_filename(image_file.filename)
        image_path = save_uploaded_file(image_file, filename)

        # Perform detection
        detection_data = detect_and_save(image_path)

        # ✅ Debugging: Print detection_data to check for issues
        print("DEBUG: Detection Data Response:", detection_data)

        # ✅ Ensure detection_results exists before proceeding
        if not detection_data or "detection_results" not in detection_data:
            return jsonify({"error": "Detection failed, no results found"}), 500

        detection_results = detection_data["detection_results"]

        # Define output filenames
        annotated_image_filename = f"annotated_{filename}"
        detection_json_filename = f"detection_{os.path.splitext(filename)[0]}.json"
        detection_json_path = os.path.join(RESULTS_FOLDER, detection_json_filename)
        annotated_image_path = os.path.join(RESULTS_FOLDER, annotated_image_filename)
        detection_json_path = os.path.join(RESULTS_FOLDER, detection_json_filename)

        # Perform grouping
        grouping_results = group_and_save(image_path, detection_results["detections"])

        # ✅ Ensure grouping_results exists before proceeding
        if not grouping_results or "grouped_image_path" not in grouping_results:
            return jsonify({"error": "Grouping failed, no results found"}), 500

        grouped_image_filename = os.path.basename(grouping_results["grouped_image_path"])
        grouped_json_filename = os.path.basename(grouping_results["grouped_json_path"])
        grouped_image_path = os.path.join(RESULTS_FOLDER, grouped_image_filename)
        grouped_json_path = os.path.join(RESULTS_FOLDER, grouped_json_filename)

        # ✅ Ensure paths exist before rendering the results page
        print(f"DEBUG: Checking if annotated image exists at: {annotated_image_path}")
        print(f"DEBUG: Checking if detection JSON exists at: {detection_json_path}")
        # ✅ Add a delay to ensure files are fully saved before checking
        time.sleep(1)
        
        # ✅ Retry checking file existence multiple times (handles slow disk writes)
        for _ in range(5):
            if os.path.exists(annotated_image_path) and os.path.exists(detection_json_path):
                break
            print("WARNING: File not found, retrying...")
            time.sleep(1)  # Wait before retrying
        
        print(f"DEBUG: Checking if file exists -> {annotated_image_path}: {os.path.exists(annotated_image_path)}")
        print(f"DEBUG: Checking if file exists -> {detection_json_path}: {os.path.exists(detection_json_path)}")

        if not os.path.exists(grouped_image_path) or not os.path.exists(grouped_json_path):
            return jsonify({"error": "Failed to save grouped results"}), 500

        # Render the results page with relative URLs
        return render_template(
            "results.html",
            grouped_image_url=f"/results/{grouped_image_filename}",
            grouped_json_url=f"/results/{grouped_json_filename}",
            annotated_image_url=f"/results/{annotated_image_filename}",
            detection_json_url=f"/results/{detection_json_filename}",
            message="Processing complete",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/results/<filename>")
def serve_result(filename):
    """
    Serve files from the RESULTS_FOLDER.
    """
    filepath = os.path.join(RESULTS_FOLDER, filename)

    # ✅ Print debug info
    print(f"DEBUG: Serving file at {filepath}")

    if not os.path.exists(filepath):
        print("ERROR: File not found!")
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(RESULTS_FOLDER, filename)


@routes.route("/results/image/<filename>", methods=["GET"])
def get_result_image(filename):
    """
    Serve processed images from the results folder.
    """
    image_path = os.path.join(RESULTS_FOLDER, filename)
    if not os.path.exists(image_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(image_path, mimetype="image/jpeg")

@routes.route("/results/json/<filename>", methods=["GET"])
def get_result_json(filename):
    """
    Serve JSON results from the results folder.
    """
    json_path = os.path.join(RESULTS_FOLDER, filename)
    if not os.path.exists(json_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(json_path, mimetype="application/json")