import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import requests

from backend2 import generate_style_image  # <-- your previous file


# ---------- Helper: Convert Uploaded Image to Base64 Data URI ----------

def image_to_data_uri(uploaded_file):
    image = Image.open(uploaded_file)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


# ---------- UI ----------

st.set_page_config(page_title="Nano Banana Style Generator", layout="centered")

st.title("🍌 Nano Banana Pro Style Generator")

st.write("Upload base image and reference image to generate styled output.")


base_image_file = st.file_uploader("Upload Base Image", type=["png", "jpg", "jpeg"])
reference_image_file = st.file_uploader("Upload Reference Image", type=["png", "jpg", "jpeg"])

flow_type = st.radio("Select Flow Type", [1, 2])

resolution = st.selectbox(
    "Select Resolution",
    ["1K", "2K", "4K"]
)

generate_button = st.button("Generate Image")


# ---------- Generate ----------

if generate_button:

    if base_image_file is None or reference_image_file is None:
        st.error("Please upload both images.")
        st.stop()

    with st.spinner("Generating image... Please wait ⏳"):

        # Convert to base64
        base_image_uri = image_to_data_uri(base_image_file)
        reference_image_uri = image_to_data_uri(reference_image_file)

        # Call backend function
        result = generate_style_image(
            base_image=base_image_uri,
            reference_image=reference_image_uri,
            flow_type=flow_type,
            resolution=resolution
        )

        fal_response = result["fal_response"]

        try:
            image_url = fal_response["images"][0]["url"]

            # Fetch image from URL
            response = requests.get(image_url)
            generated_image = Image.open(BytesIO(response.content))

            st.success("Image Generated Successfully 🎉")

            st.image(generated_image, caption="Generated Image", use_column_width=True)

            st.markdown("### Generated Prompt")
            st.code(result["prompt"])

        except Exception as e:
            st.error(f"Something went wrong: {e}")