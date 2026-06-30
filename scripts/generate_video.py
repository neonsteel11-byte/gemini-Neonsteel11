import os
import sys
import asyncio
import edge_tts

VOICE_ACTOR = "en-US-ChristopherNeural"

async def generate_voice_track(text_to_speak, output_audio_path, rate="+0%", pitch="+0Hz"):
    try:
        print(f"-> Processing voice synthesis via {VOICE_ACTOR} (Rate: {rate}, Pitch: {pitch})...")
        os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
        
        # Injecting custom speed (rate) and tone (pitch) modifiers
        communicate = edge_tts.Communicate(text_to_speak, VOICE_ACTOR, rate=rate, pitch=pitch)
        await communicate.save(output_audio_path)
        print(f"-> Tweaked voice track saved to: {output_audio_path}")
        return True
    except Exception as e:
        print(f"-> Voice compilation skipped: {str(e)}")
        return False

def compile_video_with_visuals(audio_path, output_path, display_text):
    print(f"-> Compiling video asset for {output_path}...")
    clean_text = display_text.replace("'", "'\\''").replace(":", "\\:")
    
    ffmpeg_cmd = (
        f"ffmpeg -y -f lavfi -i \"cellauto=s=720x1280:rate=1,format=gray,scale=720x1280:flags=neighbor,lut=c0='if(val,20,35)':c1=128:c2=128\" "
        f"-i {audio_path} -filter_complex "
        f"\"[0:v]drawtext=text='{clean_text}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2:"
        f"box=1:boxcolor=black@0.6:boxborderw=30:line_spacing=15:text_w=650[v]\" "
        f"-map \"[v]\" -map 1:a -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {output_path}"
    )
    os.system(ffmpeg_cmd)

def main():
    # 1. Process the Shorts track (Slightly slower for comedic pause effect)
    print("-> Generating tuned comedy roast for: Tech Megacorp...")
    short_text = "Tech Megacorp just laid off ten thousand workers to pay for an AI chatbot that hallucinates soup recipes. Brilliant move, guys."
    asyncio.run(generate_voice_track(short_text, "output/audio_short.mp3", rate="-4%", pitch="+1Hz"))
    compile_video_with_visuals("output/audio_short.mp3", "output/final_short.mp4", short_text)

    # 2. Process the Long-form track
    print("-> Generating tuned comedy roast for: EV Company...")
    long_text = "A multi-billion dollar EV company is recalling all cars because the touch screen won't let you roll down the windows. Welcome to the future where you are locked out of your own car by a software update."
    asyncio.run(generate_voice_track(long_text, "output/audio_long.mp3", rate="-2%", pitch="-2Hz"))
    compile_video_with_visuals("output/audio_long.mp3", "output/final_long.mp4", long_text)

    print("-> Production complete! Tuned assets synchronized cleanly.")

if __name__ == "__main__":
    main()
