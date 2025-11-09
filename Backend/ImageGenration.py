import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# ✅ Ensure Data folder exists
DATA_DIR = "Data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ✅ NEW WORKING API URL
API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_KEY = get_key(".env", "HuggingFaceAPIKey")

HEADERS = {
    "Authorization": f"Bearer {HF_KEY}",
    "Accept": "image/jpeg",
}

async def query(prompt, seed):
    """Send AI image request asynchronously."""
    payload = {
        "inputs": f"{prompt}, 4k, ultra realistic, sharp focus, high detail",
        "options": {"seed": seed}
    }

    response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    return response.content

async def generate_images(prompt):
    """Generate 4 images asynchronously."""
    tasks = []
    prompt_clean = prompt.replace(" ", "_")

    for _ in range(4):
        seed = randint(0, 999999)
        tasks.append(asyncio.create_task(query(prompt, seed)))

    result_images = await asyncio.gather(*tasks)

    saved_files = []
    for i, img_bytes in enumerate(result_images):
        if img_bytes.startswith(b"\xff\xd8"):  # JPEG signature
            file_path = os.path.join(DATA_DIR, f"{prompt_clean}_{i+1}.jpg")
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            print(f"✅ Saved: {file_path}")
            saved_files.append(file_path)
        else:
            print(f"❌ Invalid image {i+1} returned.")

    return saved_files

def open_images(files):
    for f in files:
        try:
            img = Image.open(f)
            print(f"🖼 Opening {f}")
            img.show()
            sleep(1)
        except:
            print(f"❌ Could not open {f}")

def GenerateImage(prompt):
    try:
        print(f"🎨 Generating images for: {prompt}")
        saved = asyncio.run(generate_images(prompt))
        open_images(saved)
    except Exception as e:
        print(f"❌ Error during image generation: {e}")

# Standalone test
if __name__ == "__main__":
    user_prompt = input("Enter an image prompt: ")
    GenerateImage(user_prompt)
