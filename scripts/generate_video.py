import os
import sys
import asyncio
import edge_tts

VOICE_ACTOR = "en-US-ChristopherNeural"

async def generate_voice_track(text_to_speak, output_audio_path, rate="+0%", pitch="+0Hz"):
    try:
        print(f"-> Processing voice synthesis via {VOICE_ACTOR}...")
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        communicate = edge_tts.Communicate(text_to_speak, VOICE_ACTOR, rate=rate, pitch=pitch)
        await communicate.save(output_audio_path)
        return True
    except Exception as e:
        print(f"-> Voice compilation skipped: {str(e)}")
        return False

def compile_video_with_animated_avatar(video_asset_path, audio_path, output_path, display_text):
    print(f"-> Merging character track with clean, smaller subtitles...")
    clean_text = display_text.replace("'", "'\\''").replace(":", "\\:")
    
    if os.path.exists(video_asset_path):
        video_input = f"-i {video_asset_path}"
    else:
        print(f"⚠️ Video loop {video_asset_path} not found. Using background image.")
        video_input = "-loop 1 -i assets/character.png"

    # FIXED SUBTITLES: Font size reduced to 26, text box width narrowed to 550, padding adjusted
    ffmpeg_cmd = (
        f"ffmpeg -y {video_input} -i {audio_path} -filter_complex "
        f"\"[0:v]drawtext=text='{clean_text}':fontcolor=white:fontsize=26:x=(w-text_w)/2:y=(h-text_h)-120:"
        f"box=1:boxcolor=black@0.75:boxborderw=15:line_spacing=8:text_w=550[v]\" "
        f"-map \"[v]\" -map 1:a -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {output_path}"
    )
    os.system(ffmpeg_cmd)

def main():
    print("-> Generating roast for: Tech Megacorp...")
    short_text = "Tech Megacorp just laid off ten thousand workers to pay for an AI chatbot that hallucinates soup recipes. Brilliant move, guys."
    asyncio.run(generate_voice_track(short_text, "output/audio_short.mp3", rate="-4%", pitch="+1Hz"))
    compile_video_with_animated_avatar("assets/animated_short.mp4", "output/audio_short.mp3", "output/final_short.mp4", short_text)

    print("-> Production complete! Subtitle layout fixed.")

if __name__ == "__main__":
    main()
