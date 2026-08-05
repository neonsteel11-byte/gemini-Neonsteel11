"""
Builds video with SMOOTH crossfades between images. NO glitchy zooms.
"""
import os, sys
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips, CompositeVideoClip

def build_video(scene_data: list, size: tuple, output_path: str, tmp_dir: str):
    clips = []
    audio_clips = []
    
    print(f"      Building video with {len(scene_data)} scenes...")
    
    for i, scene in enumerate(scene_data):
        image_path = scene["image_path"]
        audio_path = scene["audio_path"]
        duration = scene["duration"]
        
        if not os.path.exists(image_path):
            print(f"      [FATAL] Image not found: {image_path}", file=sys.stderr)
            sys.exit(1)
        
        # Simple static image clip with smooth fade
        img_clip = ImageClip(image_path).set_duration(duration)
        img_clip = img_clip.fadein(0.3).fadeout(0.3)
        clips.append(img_clip)
        
        if os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(audio_path)
                audio_clips.append(audio_clip)
            except Exception as e:
                print(f"      [!] Audio load failed: {e}")
    
    if not clips:
        print("      [FATAL] No clips to assemble", file=sys.stderr)
        sys.exit(1)
    
    print("      Concatenating scenes with smooth crossfades...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    if audio_clips:
        print("      Concatenating audio...")
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.set_audio(final_audio)
    
    print(f"      Rendering to: {output_path}")
    final_video.write_videofile(
        output_path, fps=24, codec='libx264', audio_codec='aac',
        temp_audiofile='temp-audio.m4a', remove_temp=True,
        verbose=False, logger=None
    )
    print("      ✓ Video assembled successfully!")
    final_video.close()

if __name__ == "__main__":
    print("Video builder loaded.")
