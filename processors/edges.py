# processors/edges.py
# ------------------------------------------------------------
# Core edge-detection algorithms implemented using OpenCV.
# These functions are kept independent of the user interface (UI-agnostic),
# so they can be reused in Streamlit, Tkinter, or command-line applications.
# ------------------------------------------------------------
from __future__ import annotations
import cv2
import numpy as np


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def _odd(v: int) -> int:
    """
    Ensures the kernel size is odd (required by OpenCV filters).
    Example: if v = 4, this returns 5.
    """
    v = int(v)
    return v if v % 2 == 1 else v + 1


def _gaussian_blur(gray: np.ndarray, ksize: int, sigma: float) -> np.ndarray:
    """
    Applies Gaussian blur to a grayscale image to reduce noise.
    Used as a preprocessing step for algorithms like Canny.
    """
    k = _odd(ksize)  # Guarantee kernel size is odd
    # sigma controls the intensity of the blur; higher sigma = smoother image
    return cv2.GaussianBlur(gray, (k, k), sigmaX=float(sigma), sigmaY=float(sigma))


# ------------------------------------------------------------
# CANNY EDGE DETECTION
# ------------------------------------------------------------
def run_canny(img_bgr: np.ndarray, low: int, high: int, ksize: int, sigma: float) -> np.ndarray:
    """
    Implements the Canny edge detection algorithm.
    Steps:
      1. Convert image to grayscale
      2. Optionally apply Gaussian blur (to smooth noise)
      3. Apply Canny operator with user-defined thresholds
    """
    # Convert from BGR → grayscale (Canny works on single-channel images)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur if specified (helps prevent false edges)
    if ksize > 1 or sigma > 0:
        gray = _gaussian_blur(gray, ksize, sigma)

    # Detect edges using gradient thresholds
    edges = cv2.Canny(gray, threshold1=int(low), threshold2=int(high))

    return edges  # Output: single-channel 8-bit image (edges in white)


# ------------------------------------------------------------
# SOBEL EDGE DETECTION
# ------------------------------------------------------------
def run_sobel(img_bgr: np.ndarray, ksize: int, direction: str) -> np.ndarray:
    """
    Computes Sobel edges — measures intensity gradients in X, Y, or both directions.
    Parameters:
        - ksize: kernel size (odd integer)
        - direction: 'X', 'Y', or 'Both' for gradient magnitude
    """
    # Convert to grayscale for gradient calculation
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    k = _odd(ksize)  # Ensure kernel size is valid

    # Normalize input direction (e.g., 'x' → 'X')
    direction = (direction or "Both").capitalize()

    # Determine whether to compute horizontal and/or vertical gradients
    dx = 1 if direction in ("X", "Both") else 0
    dy = 1 if direction in ("Y", "Both") else 0

    # Compute gradients in X and Y directions using Sobel operator
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k) if dx else np.zeros_like(gray, dtype=np.float64)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k) if dy else np.zeros_like(gray, dtype=np.float64)

    # If both directions are chosen, compute combined gradient magnitude
    if direction == "Both":
        mag = cv2.magnitude(gx.astype(np.float32), gy.astype(np.float32))
        # Normalize gradient magnitude to 0–255 for visualization
        mag = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        return mag.astype(np.uint8)

    # If only one direction, convert float output to displayable 8-bit image
    single = gx if dx else gy
    return cv2.convertScaleAbs(single)


# ------------------------------------------------------------
# LAPLACIAN EDGE DETECTION
# ------------------------------------------------------------
def run_laplacian(img_bgr: np.ndarray, ksize: int) -> np.ndarray:
    """
    Applies Laplacian edge detection — detects edges in all directions
    by computing the second derivative of the image intensity.
    """
    # Convert image to grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Ensure kernel size is odd (required by OpenCV)
    k = _odd(ksize)

    # Apply Laplacian filter (sensitive to rapid intensity changes)
    lap = cv2.Laplacian(gray, cv2.CV_64F, ksize=k)

    # Convert floating-point output to absolute 8-bit image for display
    return cv2.convertScaleAbs(lap)
