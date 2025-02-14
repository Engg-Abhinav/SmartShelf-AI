import os
import torch
from PIL import Image, ImageDraw
from app.utils.constants import RESULTS_FOLDER
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from app.utils.file_handler import save_json_results, get_results_path
from app.utils.constants import DETECTION_MODEL_NAME, DETECTION_THRESHOLD

# Load model and processor once (to avoid reloading for each request)
print("Loading detection model and processor...")
processor = AutoImageProcessor.from_pretrained(DETECTION_MODEL_NAME)
model = AutoModelForObjectDetection.from_pretrained(DETECTION_MODEL_NAME)
print("Detection model loaded successfully!")

def run_detection(image_path):
    """
    Perform object detection on the input image.

    Args:
        image_path (str): Path to the input image.

    Returns:
        dict: Detection results including bounding boxes, labels, and scores.
    """
    # Load the image
    print(f"Loading image: {image_path}")
    image = Image.open(image_path).convert("RGB")

    # Preprocess the image
    inputs = processor(images=image, return_tensors="pt")

    # Perform inference
    print("Running inference...")
    with torch.no_grad():
        outputs = model(**inputs)

    # Post-process the results
    target_sizes = torch.tensor([image.size[::-1]])  # (height, width)
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=DETECTION_THRESHOLD)[0]

    detections = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]  # Convert box to a list of rounded floats
        detections.append({
            "bbox": box,
            "label": model.config.id2label[label.item()],
            "score": round(score.item(), 2)
        })

    return {"image_name": os.path.basename(image_path), "detections": detections}

def save_annotated_image(image_path, detections):
    """
    Save an annotated image with bounding boxes and labels.

    Args:
        image_path (str): Path to the input image.
        detections (list): List of detection results.

    Returns:
        str: Path to the annotated image.
    """
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Draw bounding boxes and labels
    for detection in detections:
        box = detection["bbox"]
        label = detection["label"]
        score = detection["score"]
        draw.rectangle(box, outline="red", width=3)
        draw.text((box[0], box[1] - 10), f"{label}: {score:.2f}", fill="red")

    # Create the annotated image filename
        original_filename = os.path.basename(image_path)
        annotated_image_filename = f"annotated_{original_filename}"
        annotated_image_path = os.path.join(RESULTS_FOLDER, annotated_image_filename)

        # Save the annotated image
        image.save(annotated_image_path)
        return annotated_image_path

def detect_and_save(image_path):
    """
    Perform detection and save results (JSON and annotated image).

    Args:
        image_path (str): Path to the input image.

    Returns:
        dict: Detection results and paths to the annotated image and JSON file.
    """
    # Run detection
    detection_results = run_detection(image_path)

    # Save annotated image
    annotated_image_path = save_annotated_image(image_path, detection_results["detections"])

    # Save JSON results
    json_path = save_json_results("detection_results.json", detection_results)

    # Return both results and paths
    return {
        "detection_results": detection_results,
        "json_path": json_path,
        "annotated_image_path": annotated_image_path
    }

