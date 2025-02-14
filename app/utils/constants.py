import os

# Base Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))  # Adjusted to the project's root
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_FOLDER = os.path.join(STATIC_DIR, "uploads")  # Renamed to match the rest of the code
RESULTS_FOLDER = os.path.join(STATIC_DIR, "results")  # Renamed to match the rest of the code

# Model Configurations
DETECTION_MODEL_NAME = "isalia99/detr-resnet-50-sku110k"
GROUPING_MODEL_NAME = "openai/clip-vit-base-patch32"

# Result File Names
DETECTION_JSON_NAME = "detection_results.json"
ANNOTATED_IMAGE_NAME = "annotated_image.jpg"
GROUPED_IMAGE_NAME = "grouped_image.jpg"
GROUPED_JSON_NAME = "grouped_results.json"

# Detection Configuration
DETECTION_THRESHOLD = 0.6

# Grouping Configuration
GROUPING_PCA_VARIANCE = 0.95  # Retain 95% of variance
GROUPING_MIN_CLUSTER_SIZE = 2
HDBSCAN_METRIC = "euclidean"

# File Upload Limits
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 10
