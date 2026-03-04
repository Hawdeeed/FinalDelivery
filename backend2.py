import os
from dotenv import load_dotenv
from fal_client import subscribe
from openai import OpenAI

# Load .env file
load_dotenv()

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FAL_KEY = os.getenv("FAL_KEY")

if not FAL_KEY:
    raise ValueError("FAL_KEY not found in environment variables")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

class LLMService:
    def __init__(self, model="gpt-4o-mini", temperature=0.4, max_tokens=500):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens


    def generate_style_prompt2(
        self,
        reference_image: str,
        system_prompt: str = "You are a helpful assistant",
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyze this image and extract only lighting, ambience, and environment style."
                            )
                        },
                        {"type": "image_url", "image_url": {"url": reference_image}},
                    ],
                },
            ],
            temperature=0.4,  # LOWER = more controlled edits
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()
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
def generate_style_image(base_image: str, reference_image: str, flow_type: int, resolution: str = "1K"):
    llm = LLMService()
    system_prompt = """
        You are a professional photography and visual-design analyst.  
        When the user uploads an image, your job is to carefully analyze only the lighting, ambience, and environment of the image — not the product or subject.
        You must extract the scene’s visual style and convert it into a format that can be used to restyle another image while keeping its subject locked.
        Your output must be exactly two lines in this exact structure:

        Keep the watch exactly the same in size, scale, framing, position, orientation, dial, details, and strap — only change the background, lighting, and ambience.
        Replace the background, lighting, and ambience with <DETAILED_STYLE>.

        <DETAILED_STYLE> must describe only:
        • Direction and quality of light (window, studio, soft, hard, diffused, etc)
        • Color temperature AND dominant color casts (warm, cool, neutral, red, blue, neon, etc)
        • Shadow softness and contrast level
        • Reflections, specular highlights, and glow
        • Depth of field and background blur
        • Environment and materials (studio, interior, macro scene, fabric, spheres, glass, smoke, etc)
        • Overall mood (luxury, calm, cinematic, dramatic, bold, premium, editorial)

        You MUST preserve strong visual identity:
        • If the scene has intense or saturated colors, they MUST be explicitly stated.
        • If the scene contains textured or physical background elements (fabric, fur, balls, smoke, liquid, etc), they MUST be described.
        • Never neutralize a bold scene into a generic lifestyle or soft studio look.

        Do NOT mention:
        • The product
        • The subject
        • The watch
        • Any brand, logo, or object identity
        • Any colors or materials of the subject

        Write <STYLE> as a single clean, high-impact generative prompt optimized for Nano Banana, Flux, or SDXL.
        Do not add any extra text, formatting, or explanations — only the two required lines.
        """
    if flow_type == 1:
        prompt = llm.generate_style_prompt2(reference_image, system_prompt)
        fal_response = nano_banana_edit(prompt, resolution, [base_image])
    elif flow_type == 2:
        prompt = (
                "Keep the watch exactly the same as in reference image 1 — identical size, scale, zoom level, camera distance, framing, position, dial, dial interior, orientation, and strap. Do not zoom in or out. Only change the background, lighting, and ambiance to match reference image 2. Preserve the original composition. The generated image must have the same width and height as reference image 1."
            )

        # ✅ FIXED ORDER
        fal_response = nano_banana_edit(
            prompt,
            resolution,
            [base_image, reference_image],
        )
    elif flow_type == 3:
        prompt = (
                "Keep the watch and wrist exactly the same as in reference image 1 — identical size, scale, zoom level, camera distance, framing, position, dial, dial interior, orientation, wrist, wrist position and strap. Do not zoom in or out. Only change the background, lighting, wrist fabric and ambiance to match reference image 2. Preserve the original composition. The generated image must have the same width and height as reference image 1."
            )

        # ✅ FIXED ORDER
        fal_response = nano_banana_edit(
            prompt,
            resolution,
            [base_image, reference_image],
        )
        
    elif flow_type == 4:
        prompt = (
                "Edit image A to have the same background, lighting, wrist fabric and ambiance as reference image B, while keeping the watch and wrist exactly the same as in reference image 1 — identical size, scale, zoom level, camera distance, framing, position, dial, dial interior, orientation, wrist, wrist position and strap. Do not zoom in or out. Preserve the original composition. The generated image must have the same width and height as reference image A."
            )

        # ✅ FIXED ORDER
        fal_response = nano_banana_edit(
            prompt,
            resolution,
            [base_image, reference_image],
        )
        
    else:
        raise ValueError("flow_type must be 1 or 2")
    return {
        "prompt": prompt,
        "fal_response": fal_response,
    }

