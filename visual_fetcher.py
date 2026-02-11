import requests
import os

from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def fetch_images(topic, count=5):
    """Fetch multiple images from Pexels and save them."""
    print(f"   Fetching {count} visuals for '{topic}'...")
    url = f"https://api.pexels.com/v1/search?query={topic}&per_page={count}&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error fetching images:", response.text)
        return []

    data = response.json()
    photos = data.get("photos", [])
    
    if not photos:
        print("No photos found for topic.")
        return []

    saved_files = []
    if not os.path.exists("assets"):
        os.makedirs("assets")

    for i, photo in enumerate(photos):
        image_url = photo["src"]["original"]
        try:
            img_data = requests.get(image_url).content
            filename = f"assets/image_{i}.jpg"
            with open(filename, "wb") as f:
                f.write(img_data)
            saved_files.append(filename)
            # Also save as image.jpg for thumbnail/legacy support
            if i == 0:
                with open("image.jpg", "wb") as f:
                    f.write(img_data)
        except Exception as e:
            print(f"Error downloading image {i}: {e}")

    return saved_files

def fetch_image(topic):
    """Legacy support for single image fetch."""
    return fetch_images(topic, count=1)
