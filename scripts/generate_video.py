import os
import sys

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

from moviepy import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip, ImageClip

# --- IMPROVED CONFIGURATION ---
# You can now specify "img" for images OR "vid" for video clips!
ASSET_TIMELINE = [
    {"start": 0.0, "img": "assets/images/scene1_bed.png"},
    {"start": 8.0, "vid": "assets/videos/clip_5s.mp4"},          # Your 5-second video clip pattern interrupt!
    {"start": 13.0, "img": "assets/images/scene3_future.png"},
    {"start": 40.0, "img": "assets/images/scene4_wall1.png"},
    {"start": 42.0, "img": "assets/images/scene5_laptop.png"},
]

def create_scripted_video(audio_path, output_dir="output"):
    print(f"--- Starting Improved Production Render ---")
    os.makedirs(output_dir, exist_ok=True)

    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration

    clips = []

    for i, item in enumerate(ASSET_TIMELINE):
        start_time = item["start"]
        
        # Determine end time based on next item or total video length
        if i + 1 < len(ASSET_TIMELINE):
            end_time = ASSET_TIMELINE[i+1]["start"]
        else:
            end_time = total_duration

        duration = end_time - start_time

        # Check if this timeline slot is an image or a video clip
        if "img" in item:
            img_path = item["img"]
            if os.path.exists(img_path):
                clip = ImageClip(img_path).with_duration(duration)
            else:
                clip = ColorClip(size=(1920, 1080), color=(30, 30, 40)).with_duration(duration)
        
        elif "vid" in item:
            vid_path = item["vid"]
            if os.path.exists(vid_path):
                # Load video, clip it to fit the duration slot, and mute its native track to let bg_music play
                clip = VideoFileClip(vid_path).subclipped(0, duration).with_duration(duration).without_audio()
            else:
                print(f"Warning: Video asset {vid_path} missing. Using placeholder.")
                clip = ColorClip(size=(1920, 1080), color=(50, 30, 30)).with_duration(duration)

        clip = clip.with_start(start_time).with_position("center")
        clips.append(clip)

    canvas = CompositeVideoClip(clips, size=(1920, 1080)).with_duration(total_duration)
    final_video = canvas.with_audio(audio_clip)

    print("Rendering final_long.mp4 (16:9)...")
    final_video.write_videofile(
        os.path.join(output_dir, "final_long.mp4"),
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    print("Rendering final_short.mp4 (9:16 Shorts format)...")
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
    print("--- Finished! Improved videos rendered to output/ ---")

if __name__ == "__main__":
    target_audio = "assets/music/bg_music.mp3"

    if os.path.exists(target_audio):
        create_scripted_video(target_audio)
    else:
        print(f"Error: Missing audio file at {target_audio}")
