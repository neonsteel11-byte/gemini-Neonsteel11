import os
import sys

# Force static-ffmpeg paths into the environment before importing moviepy
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

from moviepy import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip, ImageClip

# --- CONFIGURATION: MAP YOUR SCRIPT TO IMAGES ---
ASSET_TIMELINE = [
    {"start": 0.0, "img": "assets/images/scene1_bed.png"},        
    {"start": 8.0, "img": "assets/images/scene2_roommates.png"},  
    {"start": 20.0, "img": "assets/images/scene3_future.png"},    
    {"start": 40.0, "img": "assets/images/scene4_wall1.png"},     
    {"start": 42.0, "img": "assets/images/scene5_laptop.png"},    
]

def create_scripted_video(audio_path, output_dir="output"):
    print(f"--- Starting Render Following Script ---")
    os.makedirs(output_dir, exist_ok=True)
    
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    
    clips = []
    
    for i, item in enumerate(ASSET_TIMELINE):
        start_time = item["start"]
        img_path = item["img"]
        
        if i + 1 < len(ASSET_TIMELINE):
            end_time = ASSET_TIMELINE[i+1]["start"]
        else:
            end_time = total_duration
            
        duration = end_time - start_time
        
        if not os.path.exists(img_path):
            clip = ColorClip(size=(1920, 1080), color=(30, 30, 40)).with_duration(duration)
        else:
            clip = ImageClip(img_path).with_duration(duration)
            
        clip = clip.with_start(start_time).with_position("center")
        clips.append(clip)
        
    canvas = CompositeVideoClip(clips, size=(1920, 1080)).with_duration(total_duration)
    final_video = canvas.with_audio(audio_clip)
    
    print("Rendering final_long.mp4...")
    final_video.write_videofile(
        os.path.join(output_dir, "final_long.mp4"), 
        fps=24, 
        codec="libx264", 
        audio_codec="aac"
    )
    
    print("Rendering final_short.mp4...")
    short_w = int(1080 * (9/16))
    x1 = int((1920 - short_w) / 2)
    
    short_video = final_video.cropped(x1=x1, y1=0, width=short_w, height=1080)
    
    short_video.write_videofile(
        os.path.join(output_dir, "final_short.mp4"), 
        fps=24, 
        codec="libx264", 
        audio_codec="aac"
    )
    
    audio_clip.close()
    print("--- Finished! Videos rendered to output/ ---")

if __name__ == "__main__":
    target_audio = "assets/music/bg_music.mp3"
    
    if os.path.exists(target_audio):
        create_scripted_video(target_audio)
    else:
        print(f"Error: Missing audio file at {target_audio}")
