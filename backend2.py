import base64
from fal_client import subscribe

def image_to_data_uri(image_path: str):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        encoded = base64.b64encode(image_bytes).decode("utf-8")

    # Change mime type if needed (jpeg/webp/etc)
    return f"data:image/png;base64,{encoded}"


def nano_banana_edit_base64(prompt: str, resolution: str, image_paths: list):

    # Convert all local images to base64 data URIs
    image_data_uris = [image_to_data_uri(path) for path in image_paths]

    result = subscribe(
        "fal-ai/nano-banana-pro/edit",
        arguments={
            "prompt": prompt,
            "resolution": resolution,
            "image_urls": image_data_uris,  # <-- Base64 here
            "num_images": 1,
            "output_format": "png",
        },
        with_logs=True
    )

    return result


if __name__ == "__main__":
    response = nano_banana_edit_base64(
        prompt="Make this person look cinematic with sunset lighting",
        resolution="1K",
        image_paths=["input1.png", "input2.png"]
    )

    print(response["data"]["images"])