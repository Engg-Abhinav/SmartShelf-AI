import os
import json
import torch
from PIL import Image, ImageDraw
from transformers import CLIPProcessor, CLIPModel
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
from hdbscan import HDBSCAN
from app.utils.file_handler import save_json_results, get_results_path
from app.utils.constants import GROUPING_PCA_VARIANCE, GROUPING_MIN_CLUSTER_SIZE
from tqdm import tqdm
import numpy as np
from skimage.feature import local_binary_pattern
from skimage.color import rgb2gray
import cv2
import matplotlib.pyplot as plt

# Load CLIP model and processor
print("Loading CLIP model and processor...")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
print("CLIP model loaded!")

def extract_color_features(image):
    """Extract color histogram features."""
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    color_histogram = np.concatenate([
        np.histogram(hsv_image[:, :, i], bins=32, range=(0, 256), density=True)[0]
        for i in range(3)
    ])
    return color_histogram

def extract_texture_features(image):
    """Extract texture features using Local Binary Patterns (LBP)."""
    gray_image = rgb2gray(image)
    lbp = local_binary_pattern(gray_image, P=8, R=1, method="uniform")
    texture_hist, _ = np.histogram(lbp, bins=np.arange(0, 11), density=True)
    return texture_hist

def generate_combined_features(image_path, detections):
    """
    Generate combined features (CLIP embeddings, color, texture) for detected objects.

    Args:
        image_path (str): Path to the input image.
        detections (list): List of detection results.

    Returns:
        np.ndarray: Combined features for clustering.
        list: Cropped images for each detection.
    """
    image = Image.open(image_path)
    embeddings = []
    color_features = []
    texture_features = []
    cropped_images = []

    for detection in tqdm(detections, desc="Processing detections"):
        bbox = detection["bbox"]
        x_min, y_min, x_max, y_max = map(int, bbox)
        cropped_image = image.crop((x_min, y_min, x_max, y_max))
        cropped_images.append(cropped_image)

        # Generate CLIP embedding
        inputs = clip_processor(images=cropped_image, return_tensors="pt")
        with torch.no_grad():
            embedding = clip_model.get_image_features(**inputs).squeeze().numpy()
        embeddings.append(embedding)

        # Extract color features
        cropped_array = np.array(cropped_image)
        color_features.append(extract_color_features(cropped_array))

        # Extract texture features
        texture_features.append(extract_texture_features(cropped_array))

    # Normalize and combine features
    embeddings = normalize(np.array(embeddings))
    color_features = normalize(np.array(color_features))
    texture_features = normalize(np.array(texture_features))
    combined_features = np.hstack([embeddings, color_features, texture_features])

    return combined_features, cropped_images

def perform_clustering(features):
    """
    Perform clustering using HDBSCAN.

    Args:
        features (np.ndarray): Combined features for clustering.

    Returns:
        np.ndarray: Cluster labels for each detection.
    """
    print("Reducing dimensionality with PCA...")
    pca = PCA(n_components=GROUPING_PCA_VARIANCE)
    reduced_features = pca.fit_transform(features)

    print("Clustering objects using HDBSCAN...")
    hdbscan_clusterer = HDBSCAN(min_cluster_size=GROUPING_MIN_CLUSTER_SIZE, metric="euclidean")
    cluster_labels = hdbscan_clusterer.fit_predict(reduced_features)

    return cluster_labels

def save_grouped_image(image_path, detections, cluster_labels):
    """
    Save grouped image with bounding boxes colored by cluster.

    Args:
        image_path (str): Path to the input image.
        detections (list): List of detection results.
        cluster_labels (np.ndarray): Cluster labels for each detection.

    Returns:
        str: Path to the grouped image.
    """
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Assign unique colors to each cluster
    cmap = plt.cm.get_cmap('tab20', max(cluster_labels) + 1)
    color_map = {label: tuple(int(c * 255) for c in cmap(label)[:3]) for label in range(max(cluster_labels) + 1)}

    for detection, cluster_id in zip(detections, cluster_labels):
        bbox = detection["bbox"]
        color = (128, 128, 128) if cluster_id == -1 else color_map[cluster_id]
        x_min, y_min, x_max, y_max = map(int, bbox)
        draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=3)
        draw.text((x_min, y_min - 10), f"Group {cluster_id}", fill=color)

    grouped_image_path = get_results_path("grouped_image.jpg")
    image.save(grouped_image_path)
    print(f"Grouped image saved at: {grouped_image_path}")
    return grouped_image_path

def group_and_save(image_path, detections):
    """
    Perform grouping and save results (JSON and grouped image).

    Args:
        image_path (str): Path to the input image.
        detections (list): List of detection results.

    Returns:
        dict: Paths to the grouped image and grouped JSON.
    """
    # Generate combined features
    features, _ = generate_combined_features(image_path, detections)

    # Perform clustering
    cluster_labels = perform_clustering(features)

    # Save grouped image
    grouped_image_path = save_grouped_image(image_path, detections, cluster_labels)

    # Save grouped JSON
    grouped_results = {
        "image_name": os.path.basename(image_path),
        "grouped_detections": [
            {"bbox": detection["bbox"], "group": int(cluster_id)}
            for detection, cluster_id in zip(detections, cluster_labels)
            if cluster_id != -1  # Exclude noise points
        ]
    }
    grouped_json_path = save_json_results("grouped_results.json", grouped_results)

    return {"grouped_image_path": grouped_image_path, "grouped_json_path": grouped_json_path}
