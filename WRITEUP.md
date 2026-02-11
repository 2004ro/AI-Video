# AI Video Generation Pipeline Write-up

## Tools Used
- **Python**: Core logic and orchestration.
- **Groq API (Llama 3)**: Generates engaging scripts and SEO metadata (Title, Description, Tags) extremely fast and for free.
- **Edge TTS**: Provides high-quality, natural-sounding voiceovers using Microsoft's free Edge text-to-speech service, avoiding expensive API costs.
- **Pexels API**: Fetches multiple high-quality stock visuals to create a dynamic slideshow for the video background.
- **Pillow (PIL)**: Programmatically generates thumbnails by overlaying text on the source image, resizing for Shorts (9:16).
- **MoviePy**: Handles video editing, compositing the images and audio, and rendering the final portrait-mode video (1080x1920) with high-impact captions.

## Biggest Challenge
The most significant challenge was **synchronization and asset orchestration**. Ensuring the subtitles (SRT) perfectly matched the spoken audio while managing a sequence of visual assets to cover the full duration required precise timing calculations and frame cropping.

## Future Improvements
1.  **AI Image Generation**: Integrate APIs like DALL-E or Stable Diffusion to generate unique visuals.
2.  **Background Music**: Adding a background music track with auto-ducking.
3.  **YouTube Upload Automation**: Automating the upload process with the generated metadata.
4.  **Transitions**: Adding zoom effects (Ken Burns) or smoother transitions between scenes.
