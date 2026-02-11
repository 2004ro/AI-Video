from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import textwrap

def generate_thumbnail(image_path, text, output_path="thumbnail.jpg"):
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Resize to YouTube Shorts thumbnail size (optional, but good for consistency)
        # Shorts thumbnails are often viewed vertically, but standard thumbnails are 16:9.
        # Since this is a short, the video frame itself is the thumbnail usually.
        # But let's create a 9:16 'cover' image.
        target_size = (1080, 1920)
        img = img.resize(target_size, Image.Resampling.LANCZOS)

        # Darken the image to make text pop
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.6)

        draw = ImageDraw.Draw(img)

        # Try to load a font, fallback to default
        try:
            # Arial is common on Windows
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()

        # Wrap text
        lines = textwrap.wrap(text, width=20)
        
        # Calculate text position (center)
        # Simple vertical centering approach
        current_h = 600 # Start a bit down
        for line in lines:
            # getting bounding box of text
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (target_size[0] - text_width) / 2
            draw.text((x, current_h), line, font=font, fill="white")
            current_h += text_height + 20

        img.save(output_path)
        print(f"Thumbnail saved to {output_path}")

    except Exception as e:
        print(f"Error creating thumbnail: {e}")

if __name__ == "__main__":
    generate_thumbnail("image.jpg", "AI Video\nGenerator")
