import edge_tts
import asyncio
import io
import ssl
import os

# Disable SSL verification globally for edge-tts
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''

# Try to set SSL context for aiohttp
try:
    import aiohttp
    aiohttp.TCPConnector = lambda **kwargs: aiohttp.TCPConnector(limit=1, ttl_dns_cache=300, **kwargs)
except:
    pass

# Helper to format time for SRT: HH:MM:SS,mmm
def format_time(hns):
    seconds = hns / 10_000_000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    
    # We will accumulate audio data and subtitle info
    audio_data = bytearray()
    first_word_time = None
    last_word_time = None
    current_line = []
    subtitles = []
    
    sub_index = 1
    
    # Function to save a subtitle line
    def save_subtitle_line(start, end, text):
        nonlocal sub_index
        if start is not None and end is not None:
             # Ensure duration is at least a bit visible
            if end - start < 5_000_000: # less than 0.5s
                end = start + 5_000_000
            
            subtitles.append(f"{sub_index}\n{format_time(start)} --> {format_time(end)}\n{text}\n\n")
            sub_index += 1

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            # chunk has ['offset', 'duration', 'text']
            # offset and duration are in 100ns units
            start = chunk["offset"]
            duration = chunk["duration"]
            word = chunk["text"]
            end = start + duration
            
            # Subtitle logic: group words
            if len(" ".join(current_line + [word])) > 40:
                # Flush current line
                save_subtitle_line(first_word_time, last_word_time, " ".join(current_line))
                current_line = [word]
                first_word_time = start
                last_word_time = end
            else:
                current_line.append(word)
                if first_word_time is None:
                    first_word_time = start
                last_word_time = end

    # Flush remaining text
    if current_line:
        save_subtitle_line(first_word_time, last_word_time, " ".join(current_line))
        
    # Write files
    with open("voice.mp3", "wb") as f:
        f.write(audio_data)
        
    with open("final_video.srt", "w", encoding="utf-8") as f:
        f.writelines(subtitles)

    print("Voice and Subtitles generated.")
