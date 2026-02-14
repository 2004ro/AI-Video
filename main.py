import asyncio
import json
import os
import sys
import shutil

from script_generator import generate_script
from voice_generator import generate_voice
from visual_fetcher import fetch_images
from video_editor import create_video
from metadata_generator import generate_metadata
from thumbnail_generator import generate_thumbnail

def cleanup():
    """Remove files from previous runs to ensure fresh generation."""
    files_to_remove = ["voice.mp3", "final_video.srt", "image.jpg", "thumbnail.jpg", "metadata.json", "final_video.mp4"]
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists("assets"):
        shutil.rmtree("assets")

if __name__ == "__main__":
    try:
        topic = input("Enter Video Topic: ")
        
        print(f"\n--- Starting Pipeline for '{topic}' ---")
        
        # 0. Cleanup
        print("0. Cleaning up previous run...")
        cleanup()

        # 1. Script
        print("1. Generating Script...")
        script = generate_script(topic)
        if not script:
            raise Exception("Script generation failed.")
        print(f"   Script length: {len(script)} chars")

        # 2. Voice & Subtitles
        print("2. Generating Voice & Subtitles...")
        asyncio.run(generate_voice(script))
        
        # 3. Visuals
        print("3. Fetching Visuals...")
        images = fetch_images(topic, count=8) # Fetch 8 images for variety
        
        # --- IMPROVEMENT: FALLBACK MECHANISM ---
        if not images or len(images) == 0:
            print("   ⚠️ Pexels API failed or found no images. Using fallback generator...")
            from PIL import Image
            if not os.path.exists("assets"): os.makedirs("assets")
            
            # Generate 3 fallback solid-color images
            colors = [(40, 44, 52), (100, 149, 237), (255, 127, 80)] # Dark, Blue, Coral
            images = []
            for i, color in enumerate(colors):
                fallback_path = f"assets/image_{i}.jpg"
                img = Image.new('RGB', (1080, 1920), color=color)
                img.save(fallback_path)
                # Save first one as image.jpg for thumbnail fallback too
                if i == 0:
                    img.save("image.jpg")
                images.append(fallback_path)
            print(f"   Success: Generated {len(images)} fallback visual(s).")
        # ---------------------------------------
        
        # 4. Thumbnail
        print("4. Generating Thumbnail...")
        # image.jpg is saved by fetch_images(topic, count=1) or the first image of fetch_images
        thumbnail_base = "image.jpg"
        if not os.path.exists(thumbnail_base):
            # Fallback if image.jpg wasn't created
            asset_dir = "assets"
            if os.path.exists(asset_dir) and os.listdir(asset_dir):
                thumbnail_base = os.path.join(asset_dir, os.listdir(asset_dir)[0])
        
        generate_thumbnail(thumbnail_base, topic)
        
        # 5. Metadata
        print("5. Generating SEO Metadata...")
        metadata = generate_metadata(topic)
        if metadata:
            with open("metadata.json", "w") as f:
                f.write(metadata)
            try:
                meta_obj = json.loads(metadata)
                print(f"   Title: {meta_obj.get('title')}")
            except:
                pass

        # 6. Video Editor
        print("6. Creating Video (this may take a moment)...")
        create_video()

        print("\n--- Pipeline Complete! ---")
        print(f"Video: {os.path.abspath('final_video.mp4')}")
        print(f"Subs:  {os.path.abspath('final_video.srt')}")
        print(f"Thumb: {os.path.abspath('thumbnail.jpg')}")
        print(f"Meta:  {os.path.abspath('metadata.json')}")

        # Play video
        if os.name == 'nt':
            print("\nPlaying video...")
            try:
                os.startfile("final_video.mp4")
            except Exception as e:
                print(f"Could not auto-play: {e}")

    except Exception as e:
        print(f"\n❌ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()
