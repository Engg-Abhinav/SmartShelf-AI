import cv2
import numpy as np
from PIL import Image

def resize_image(image_path, target_size=(800, 800)):
    """
    Resize the image to a given target size.
    :param image_path: Path to the image file
    :param target_size: Tuple specifying (width, height)
    :return: Resized image as a PIL Image object
    """
    image = Image.open(image_path)
    image = image.resize(target_size, Image.ANTIALIAS)
    return image

def convert_image_to_array(image):
    """
    Convert a PIL image to a NumPy array.
    :param image: PIL image object
    :return: NumPy array of the image
    """
    return np.array(image)

def clean_image(image):
    """
    Apply basic cleaning to an image (e.g., noise reduction).
    :param image: PIL image object
    :return: Cleaned image as a PIL Image object
    """
    img_array = np.array(image)
    img_array = cv2.GaussianBlur(img_array, (5, 5), 0)
    return Image.fromarray(img_array)
