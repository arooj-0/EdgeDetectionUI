# app.py
# ------------------------------------------------------------
# Streamlit UI: upload → pick algorithm → tweak sliders → see result
# (Live update only – recomputes automatically on slider change)
# ------------------------------------------------------------

import io
import streamlit as st
from PIL import Image

# Import helper functions for image conversion between PIL and OpenCV
from utils.image_io import pil_to_cv2, cv2_to_pil
# Import edge detection algorithms (Canny, Sobel, Laplacian)
from processors.edges import run_canny, run_sobel, run_laplacian


# --------- Page setup ---------
st.set_page_config(page_title="Interactive Edge Detection UI", layout="wide")  # Configure Streamlit page
st.title("Interactive Edge Detection UI")  # Main heading
st.caption("CS-4218 • Visual experimentation with Sobel, Laplacian, and Canny")  # Subtitle / course reference


# --------- File upload section ---------
uploaded = st.file_uploader(
    "Upload an image (JPG/PNG/BMP)",  # Upload prompt
    type=["jpg", "jpeg", "png", "bmp"]  # Restrict file types
)

# Stop execution if no file uploaded
if uploaded is None:
    st.info("Upload an image to get started.")  # User instruction
    st.stop()

# Open uploaded image as PIL and convert to RGB mode
pil_img = Image.open(uploaded).convert("RGB")

# Convert image from PIL RGB → OpenCV BGR (for OpenCV processing)
bgr = pil_to_cv2(pil_img)


# --------- Sidebar controls ---------
st.sidebar.header("Controls")  # Sidebar title for settings

# Select which algorithm to apply
algo = st.sidebar.radio(
    "Edge Detection Algorithm",
    ["Canny", "Sobel", "Laplacian"],
    help="Select which algorithm to apply."  # Tooltip for better UX
)

# Dictionary to store current slider parameter values
params = {}

# --------- Algorithm parameter controls ---------
# CANNY PARAMETERS
if algo == "Canny":
    st.sidebar.subheader("Canny Parameters")
    # Kernel size and sigma control Gaussian blur applied before edge detection
    params["ksize"] = st.sidebar.slider("Gaussian kernel size", 1, 15, 5, step=2,
                                        help="Odd values only. Used for pre-blur.")
    params["sigma"] = st.sidebar.slider("Gaussian sigma", 0.0, 5.0, 1.0, step=0.1)
    # Thresholds define edge sensitivity
    params["low"]   = st.sidebar.slider("Lower threshold", 0, 255, 100, step=1)
    params["high"]  = st.sidebar.slider("Upper threshold", 0, 255, 200, step=1)

# SOBEL PARAMETERS
elif algo == "Sobel":
    st.sidebar.subheader("Sobel Parameters")
    # Kernel size defines gradient window; direction chooses axis
    params["ksize"]     = st.sidebar.slider("Kernel size", 1, 15, 3, step=2)
    params["direction"] = st.sidebar.selectbox("Gradient direction", ["X", "Y", "Both"])

# LAPLACIAN PARAMETERS
else:  # Laplacian
    st.sidebar.subheader("Laplacian Parameters")
    params["ksize"] = st.sidebar.slider("Kernel size", 1, 15, 3, step=2)


# --------- Image processing (always recomputes) ---------
# The algorithm automatically re-runs every time a slider or input changes
if algo == "Canny":
    out = run_canny(
        bgr,
        low=params["low"],
        high=params["high"],
        ksize=params["ksize"],
        sigma=params["sigma"]
    )
elif algo == "Sobel":
    out = run_sobel(
        bgr,
        ksize=params["ksize"],
        direction=params["direction"]
    )
else:
    out = run_laplacian(
        bgr,
        ksize=params["ksize"]
    )


# --------- Image display section ---------
# Use two columns: left for input, right for processed output
left, right = st.columns(2, gap="large")

# Left column shows original image
with left:
    st.subheader("Input")
    st.image(pil_img, use_container_width=True)

# Right column shows processed image
with right:
    st.subheader("Output")
    # clamp=True ensures proper grayscale display (prevents automatic scaling)
    st.image(out, clamp=True, use_container_width=True)


# --------- Download result section ---------
# Convert processed NumPy image (OpenCV BGR) back to PIL for saving
out_pil = cv2_to_pil(out)

# Create a temporary in-memory buffer to store output PNG
buf = io.BytesIO()
out_pil.save(buf, format="PNG")

# Download button lets the user save processed image
st.download_button(
    "Download output (PNG)",
    data=buf.getvalue(),
    file_name="edges.png",
    mime="image/png"
)

# Footer note for attribution
st.caption("Built with OpenCV + Streamlit.")
