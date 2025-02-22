import os
import json
from werkzeug.utils import secure_filename
from app.utils.constants import ALLOWED_EXTENSIONS, UPLOADS_FOLDER, RESULTS_FOLDER

# Ensure directories exist
os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def is_allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(upload_file, filename):
    # Define the upload path
    upload_path = os.path.join(UPLOADS_FOLDER, filename)
    upload_file.save(upload_path)
    return upload_path


def get_results_path(filename):
    """Get the full path to a result file."""
    return os.path.join(RESULTS_FOLDER, filename)

def save_json_results(filename, data):
    """Save JSON results to the results directory."""
    file_path = get_results_path(filename)

    try:
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"DEBUG: JSON file saved successfully at {file_path}")
    except Exception as e:
        print(f"ERROR: Failed to save JSON file - {e}")

    # Ensure the file actually exists after saving
    if not os.path.exists(file_path):
        print(f"ERROR: JSON file missing after saving! {file_path}")

    return file_path
