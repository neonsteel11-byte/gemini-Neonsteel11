import os
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip

def create_outputs(audio_path, video_asset_path="assets/background_loop.mp4", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    video_clip = VideoFileClip(video_asset_path)
    audio_clip = AudioFileClip(audio_path)
    
    final_duration = audio_clip.duration
    looped_video = video_clip.loop(duration=final_duration)
    
    # 1. GENERATE SHORTS FORMAT (9:16)
    short_w = int(looped_video.h * (9/16))
    short_clip = looped_video.crop(x_center=looped_video.w/2, width=short_w, height=looped_video.h)
    short_clip = short_clip.set_audio(audio_clip)
    short_clip.write_videofile(os.path.join(output_dir, "final_short.mp4"), fps=24, codec="libx264")
    
    # 2. GENERATE LONG FORMAT (16:9)
    long_bg = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=final_duration)
    resized_square = looped_video.resize(height=1080)
    long_clip = CompositeVideoClip([long_bg, resized_square.set_position("center")])
    long_clip = long_clip.set_audio(audio_clip)
    long_clip.write_videofile(os.path.join(output_dir, "final_long.mp4"), fps=24, codec="libx264")
    
    video_clip.close()
    audio_clip.close()

if __name__ == "__main__":
    # Test execution if audio asset is present
    if os.path.exists("music/background_music.mp3"):
        create_outputs("music/background_music.mp3")
