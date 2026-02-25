import streamlit as st
import requests
from backend import generate_style_image
import base64

st.set_page_config(page_title="Watch Style Editor", layout="wide")
st.title("🖼 Watch Style Editor")

# --- Upload Images ---
base_file = st.file_uploader("Base Image", type=["png", "jpg", "jpeg"])
ref_file = st.file_uploader("Reference Image", type=["png", "jpg", "jpeg"])
flow_type = st.selectbox("Flow Type", [1, 2])
resolution = st.selectbox("Resolution", ["1K", "2K", "4K"])

def encode_image(file):
    bytes_data = file.read()
    return "data:image/png;base64," + base64.b64encode(bytes_data).decode()

if st.button("Generate"):
    if not base_file or not ref_file:
        st.error("Upload both images")
        st.stop()

    base_encoded = encode_image(base_file)
    ref_encoded = encode_image(ref_file)

    with st.spinner("Generating..."):
        try:
            result = generate_style_image(
                base_image=base_encoded,
                reference_image=ref_encoded,
                flow_type=flow_type,
                resolution=resolution
            )
        except Exception as e:
            st.error("Generation failed")
            st.write(e)
            st.stop()

    # --- Show Prompt ---
    st.subheader("Generated Prompt")
    st.code(result["prompt"])

    # --- Show Image ---
    image_url = result["fal_response"]["images"][0]["url"]
    st.image(image_url, caption="Generated Image", use_column_width=True)

        # Download button
    st.download_button(
        label="Download Image",
        data=requests.get(image_url).content,
        file_name="generated.png",
        mime="image/png"
    )
        
      