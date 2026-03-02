import os
from dotenv import load_dotenv
from fal_client import subscribe

# Load .env file
load_dotenv()

# Get API key from environment
FAL_KEY = os.getenv("FAL_KEY")

if not FAL_KEY:
    raise ValueError("FAL_KEY not found in environment variables")

# Set it for fal-client
os.environ["FAL_KEY"] = FAL_KEY


def nano_banana_edit(prompt, resolution, image_urls):

    result = subscribe(
        "fal-ai/nano-banana-pro/edit",
        arguments={
            "prompt": prompt,
            "resolution": resolution,
            "image_urls": image_urls,
            "num_images": 1,
        },
        with_logs=True
    )

    return result


if __name__ == "__main__":

    response = nano_banana_edit(
        prompt="Cinematic sunset lighting",
        resolution="1K",
        image_urls=[
            "https://storage.googleapis.com/falserverless/example_inputs/nano-banana-edit-input.png"
        ]
    )

    print(response["data"])