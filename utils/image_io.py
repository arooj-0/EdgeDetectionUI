# utils/image_io.py
# ------------------------------------------------------------
# Helper functions to safely convert between PIL (used by Streamlit)
# and OpenCV (used for image processing).
#
# Streamlit expects images in RGB format (as PIL or NumPy arrays),
# while OpenCV internally uses BGR order.
# These converters ensure color consistency between the two libraries.
# ------------------------------------------------------------

from __future__ import annotations
import numpy as np
import cv2
from PIL import Image


# ------------------------------------------------------------
# Convert from PIL → OpenCV
# ------------------------------------------------------------
def pil_to_cv2(img_pil: Image.Image) -> np.ndarray:
    """
    Converts an image from PIL format (used in Streamlit)
    to an OpenCV-compatible NumPy array (BGR color order).
    """
    # Convert PIL Image to a NumPy array in standard RGB order
    arr = np.array(img_pil.convert("RGB"))

    # Convert color order from RGB → BGR for OpenCV processing
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


# ------------------------------------------------------------
# Convert from OpenCV → PIL
# ------------------------------------------------------------
def cv2_to_pil(img_cv: np.ndarray) -> Image.Image:
    """
    Converts an image from OpenCV format (BGR or grayscale)
    back to a PIL Image (RGB) for Streamlit display or saving.
    """
    # If the input image is single-channel (grayscale),
    # convert it to a 3-channel RGB image
    if img_cv.ndim == 2:
        rgb = cv2.cvtColor(img_cv, cv2.COLOR_GRAY2RGB)
    else:
        # If already 3-channel, swap color order from BGR → RGB
        rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

    # Return a new PIL Image object built from the RGB NumPy array
    return Image.fromarray(rgb)
