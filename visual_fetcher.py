import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_images(topic, count=5, retries=3):
    """
    Fetch multiple images from Pexels with retry logic and error handling.
    If the API fails, it returns an empty list which the main pipeline handles.
    """
    if not PEXELS_API_KEY:
        print("⚠️ Warning: PEXELS_API_KEY not found in environment.")
        return []

    print(f"   Fetching {count} visuals for '{topic}'...")
    url = f"https://api.pexels.com/v1/search?query={topic}&per_page={count}&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                
                if not photos:
                    print(f"   No photos found for '{topic}' on Pexels.")
                    return []

                saved_files = []
                if not os.path.exists("assets"):
                    os.makedirs("assets")

                for i, photo in enumerate(photos):
                    image_url = photo["src"]["large2x"] # Better quality than original for faster download
                    try:
                        img_data = requests.get(image_url, timeout=10).content
                        filename = f"assets/image_{i}.jpg"
                        with open(filename, "wb") as f:
                            f.write(img_data)
                        saved_files.append(filename)
                        
                        # Legacy support for single image
                        if i == 0:
                            with open("image.jpg", "wb") as f:
                                f.write(img_data)
                    except Exception as e:
                        print(f"   ❌ Error downloading image {i}: {e}")
                
                return saved_files
            
            elif response.status_code == 429:
                print(f"   ⚠️ Rate limited. Waiting 5s... (Attempt {attempt+1}/{retries})")
                time.sleep(5)
            else:
                print(f"   ⚠️ Pexels API Error {response.status_code}: {response.text}")
                time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Connection error: {e}. Retrying... (Attempt {attempt+1}/{retries})")
            time.sleep(2)

    print("   ❌ Failed to fetch images after multiple attempts.")
    return []

def fetch_image(topic):
    """Legacy support for single image fetch."""
    return fetch_images(topic, count=1)
