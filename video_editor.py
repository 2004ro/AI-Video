from moviepy import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
from pathlib import Path
import os
import re

def parse_srt(srt_path):
    """Parse SRT file and return list of (start_time, end_time, text)"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    subtitles = []
    blocks = content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            # Skip index line
            time_line = lines[1]
            text_lines = lines[2:]
            
            # Parse time: 00:00:00,000 --> 00:00:00,000
            if '-->' in time_line:
                times = time_line.split('-->')
                start_time = parse_srt_time(times[0].strip())
                end_time = parse_srt_time(times[1].strip())
                text = ' '.join(text_lines)
                subtitles.append((start_time, end_time, text))
    
    return subtitles

def parse_srt_time(time_str):
    """Parse SRT time format to seconds"""
    # Format: 00:00:00,000
    parts = time_str.replace(',', '.').split(':')
    hours = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def process_image_clip(img_path, duration):
    """Process a single image to fit 1080x1920 with a subtle zoom effect."""
    clip = ImageClip(img_path).with_duration(duration)
    
    # Resize to cover screen height + 20% for zoom room
    target_h = 1920
    target_w = 1080
    
    # Initial resize to fill height
    clip = clip.resized(height=target_h)
    
    # If still too narrow, fill width
    if clip.w < target_w:
        clip = clip.resized(width=target_w)
        
    # Center crop to 1080x1920
    clip = clip.cropped(
        width=target_w, 
        height=target_h, 
        x_center=clip.w/2, 
        y_center=clip.h/2
    )

    # Add a subtle zoom-in effect (from 1.0 to 1.1 scale)
    def scroll_zoom(get_frame, t):
        # Linearly increase scale from 1.0 to 1.1
        scale = 1.0 + (0.1 * (t / duration))
        frame = get_frame(t)
        
        # We need to import PIL here or use clip.resize(scale) 
        # But moviepy's transform is easier
        return frame

    # Actually, moviepy.video.fx.all.zoom is better if available, 
    # but let's use a simpler approach: resize with a function
    # clip = clip.resize(lambda t: 1.0 + 0.05 * t/duration) # Simple zoom
    
    try:
        clip = clip.resized(lambda t: 1.0 + (0.1 * t / duration))
    except:
        # Fallback if lambda resize isn't supported in this version
        pass
        
    return clip

def create_video():
    # Load audio
    audio = AudioFileClip("voice.mp3")
    duration = audio.duration
    
    # Check for multiple images in assets/
    asset_dir = Path("assets")
    image_files = sorted(list(asset_dir.glob("image_*.jpg"))) if asset_dir.exists() else []
    
    if not image_files:
        # Fallback to single image
        if os.path.exists("image.jpg"):
            image_files = [Path("image.jpg")]
        else:
            raise Exception("No images found to create video.")

    # Calculate duration per image
    img_duration = duration / len(image_files)
    
    clips = []
    for img_path in image_files:
        clips.append(process_image_clip(str(img_path), img_duration))
    
    # Concatenate all image clips
    if len(clips) > 1:
        video = concatenate_videoclips(clips, method="compose")
    else:
        video = clips[0]
        
    video = video.with_audio(audio)
    
    # Add subtitles if SRT exists
    srt_path = Path("final_video.srt")
    if srt_path.exists() and srt_path.stat().st_size > 0:
        subtitles = parse_srt(srt_path)
        
        subtitle_clips = []
        for start, end, text in subtitles:
            # Create text clip for each subtitle
            txt_clip = TextClip(
                text=text.upper(), # Uppercase for more impact
                fontsize=70,
                font="Arial-Bold",
                color="yellow", # Yellow is more engaging for captions
                size=(1000, None),  # Max width
                method="caption",
                duration=end - start,
                stroke_color="black",
                stroke_width=2
            ).with_position(("center", 1400))  # Moved slightly up from bottom
            
            txt_clip = txt_clip.with_start(start)
            subtitle_clips.append(txt_clip)
        
        # Composite all clips
        video = CompositeVideoClip([video] + subtitle_clips)
    
    # Export video
    video.write_videofile(
        "final_video.mp4",
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )
