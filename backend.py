import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FAL_KEY = os.getenv("FAL_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not FAL_KEY:
    raise ValueError("FAL_KEY not found in environment variables")


# ==============================
# LLM SERVICE
# ==============================
class LLMService:
    def __init__(self, model="gpt-4o-mini", temperature=0.4, max_tokens=500):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_prompt(self, base_image: str, reference_image: str, system_prompt: str):
        """
        base_image and reference_image should be base64 or URL
        """
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Generate a precise structured image editing prompt."},
                        {"type": "input_image", "image_url": base_image},
                        {"type": "input_image", "image_url": reference_image},
                    ],
                },
            ],
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

        return response.output_text.strip()


# ==============================
# FAL IMAGE SERVICE
# ==============================
class FalImageService:
    FAL_ENDPOINT = "https://fal.run/fal-ai/nano-banana-pro/edit"

    def __init__(self):
        self.api_key = FAL_KEY

    def generate_image(self, prompt: str, image_urls: list[str], resolution="1K"):
        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": prompt,
            "image_urls": image_urls,
            "resolution": resolution,
            "num_images": 1,
            "aspect_ratio": "auto",
            "output_format": "png",
            "sync_mode": True,
        }

        response = requests.post(self.FAL_ENDPOINT, headers=headers, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()


# ==============================
# MAIN FUNCTION
# ==============================
def generate_style_image(base_image: str, reference_image: str, flow_type: int, resolution: str = "1K"):
    llm = LLMService()
    fal = FalImageService()

    SYSTEM_PROMPT = """
    You are a professional photography and visual-design analyst.
    Analyze ONLY the lighting, ambience, and environment — not the product.
    Output EXACTLY two lines:

    Keep the watch exactly the same in size, scale, framing, position, orientation, dial, details, and strap — only change the background, lighting, and ambience.
    Replace the background, lighting, and ambience with <DETAILED_STYLE>.

    <DETAILED_STYLE> must include:
    - Light direction and quality
    - Color temperature and color cast
    - Shadow softness and contrast
    - Reflections and highlights
    - Depth of field
    - Environment materials
    - Mood and atmosphere

    Do not mention product identity or brand.
    Do not add extra text.
    """

    if flow_type == 1:
        prompt = llm.generate_prompt(base_image, reference_image, SYSTEM_PROMPT)
        fal_response = fal.generate_image(prompt, [base_image], resolution)
    elif flow_type == 2:
        prompt = llm.generate_prompt(base_image, reference_image, SYSTEM_PROMPT)
        fal_response = fal.generate_image(prompt, [base_image, reference_image], resolution)
    else:
        raise ValueError("flow_type must be 1 or 2")

    return {
        "prompt": prompt,
        "fal_response": fal_response,
    }