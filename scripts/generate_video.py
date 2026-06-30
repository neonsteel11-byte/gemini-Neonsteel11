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
    print(f"-> Merging animated character track with dynamic text overlays...")
    clean_text = display_text.replace("'", "'\\''").replace(":", "\\:")
    
    # Check if the animated clip exists, fall back to a black background if not found yet
    if os.path.exists(video_asset_path):
        video_input = f"-i {video_asset_path}"
    else:
        print(f"⚠️ Animated video {video_asset_path} not found. Defaulting to temporary canvas.")
        video_input = "-f lavfi -i color=c=black:s=720x1280"

    ffmpeg_cmd = (
        f"ffmpeg -y {video_input} -i {audio_path} -filter_complex "
        f"\"[0:v]drawtext=text='{clean_text}':fontcolor=white:fontsize=38:x=(w-text_w)/2:y=(h-text_h)-180:"
        f"box=1:boxcolor=black@0.7:boxborderw=20:line_spacing=12:text_w=600[v]\" "
        f"-map \"[v]\" -map 1:a -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {output_path}"
    )
    os.system(ffmpeg_cmd)

def main():
    # 1. Process Shorts Track
    print("-> Generating tuned comedy roast for: Tech Megacorp...")
    short_text = "Tech Megacorp just laid off ten thousand workers to pay for an AI chatbot that hallucinates soup recipes. Brilliant move, guys."
    asyncio.run(generate_voice_track(short_text, "output/audio_short.mp3", rate="-4%", pitch="+1Hz"))
    
    # Point this to where you save your animated character video clip
    compile_video_with_animated_avatar("assets/animated_short.mp4", "output/audio_short.mp3", "output/final_short.mp4", short_text)

    # 2. Process Long Track
    print("-> Generating tuned comedy roast for: EV Company...")
    long_text = "A multi-billion dollar EV company is recalling all cars because the touch screen won't let you roll down the windows. Welcome to the future where you are locked out by a software update."
    asyncio.run(generate_voice_track(long_text, "output/audio_long.mp3", rate="-2%", pitch="-2Hz"))
    
    compile_video_with_animated_avatar("assets/animated_long.mp4", "output/audio_long.mp3", "output/final_long.mp4", long_text)

    print("-> Production complete! Animated pipeline updated.")

if __name__ == "__main__":
    main()
