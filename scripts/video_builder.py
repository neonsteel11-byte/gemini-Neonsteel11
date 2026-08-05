"""
Builds the final video with smooth Ken Burns transitions.
"""
import os
import sys
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips, 
    CompositeVideoClip
)
from moviepy.video.fx.all import crop, resize

def create_ken_burns_clip(image_path, duration, size):
    """Creates a slow zoom-in effect (Ken Burns) for a static image."""
    try:
        clip = ImageClip(image_path).set_duration(duration)
        zoomed_clip = clip.fx(resize, lambda t: 1.0 + 0.1 * (t / duration))
        final_clip = crop(zoomed_clip, width=size[0], height=size[1], x_center=size[0]//2, y_center=size[1]//2)
        return final_clip.set_duration(duration)
    except Exception as e:
        print(f"      [WARNING] Ken Burns failed for {image_path}: {e}. Using static image.")
        return ImageClip(image_path).set_duration(duration)

def build_video(scene_data: list, size: tuple, output_path: str, tmp_dir: str):
    """Assembles video with smooth crossfade transitions between scenes."""
    clips = []
    audio_clips = []
    
    print(f"      Building video with {len(scene_data)} scenes...")
    
    for i, scene in enumerate(scene_data):
        image_path = scene["image_path"]
        image_path_2 = scene.get("image_path_2")
        audio_path = scene["audio_path"]
        duration = scene["duration"]
        
        if not os.path.exists(image_path):
            print(f"      [FATAL] Image not found: {image_path}", file=sys.stderr)
            sys.exit(1)
            
        base_clip = create_ken_burns_clip(image_path, duration, size)
        
        if image_path_2 and os.path.exists(image_path_2) and image_path_2 != image_path:
            try:
                clip1 = create_ken_burns_clip(image_path, duration / 2, size)
                clip2 = create_ken_burns_clip(image_path_2, duration / 2, size)
                final_scene_clip = concatenate_videoclips([
                    clip1.fadeout(0.5),
                    clip2.fadein(0.5).set_start((duration / 2) - 0.5)
                ], method="compose").set_duration(duration)
            except Exception as e:
                print(f"      [WARNING] Transition failed: {e}. Using static image.")
                final_scene_clip = base_clip
        else:
            final_scene_clip = base_clip
            
        final_scene_clip = final_scene_clip.fadein(0.2).fadeout(0.2)
        clips.append(final_scene_clip)
        
        if os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(audio_path)
                audio_clips.append(audio_clip)
            except Exception as e:
                print(f"      [WARNING] Audio load failed: {e}")
                
    if not clips:
        print("      [FATAL] No valid clips to assemble", file=sys.stderr)
        sys.exit(1)
        
    print("      Concatenating scenes...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    # FIX: Use concatenate_audioclips for audio, not concatenate_videoclips
    if audio_clips:
        print("      Concatenating audio...")
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.set_audio(final_audio)
        
    print(f"      Rendering final video to: {output_path}")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        verbose=False,
        logger=None
    )
    print("      ✓ Video assembled successfully!")
    final_video.close()

if __name__ == "__main__":
    print("Video builder loaded successfully.")
