"""
Builds the final video with smooth Ken Burns (zoom/pan) transitions and crossfades.
Industry standard for high-retention faceless YouTube channels.
"""
import os
import sys
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import crop, resize

def create_ken_burns_clip(image_path, duration, size):
    """Creates a slow zoom-in effect (Ken Burns) for a static image."""
    clip = ImageClip(image_path).set_duration(duration)
    
    # Start at 100% size, slowly zoom to 110%
    def zoom_effect(get_frame, t):
        zoom_factor = 1.0 + (0.1 * (t / duration))
        img = get_frame(t)
        # Simple resize for zoom effect (moviepy handles this efficiently)
        return resize(clip, zoom_factor).get_frame(t)
        
    # Apply the effect and center crop to target size
    zoomed_clip = clip.fx(resize, lambda t: 1.0 + 0.1 * (t / duration))
    final_clip = crop(zoomed_clip, width=size[0], height=size[1], x_center=size[0]//2, y_center=size[1]//2)
    
    return final_clip.set_duration(duration)

def build_video(scene_data: list, size: tuple, output_path: str, tmp_dir: str):
    """Assembles video with smooth crossfade transitions between scenes."""
    clips = []
    audio_clips = []
    
    print(f"      Building video with {len(scene_data)} scenes (with smooth transitions)...")
    
    for i, scene in enumerate(scene_data):
        image_path = scene["image_path"]
        image_path_2 = scene.get("image_path_2")
        audio_path = scene["audio_path"]
        duration = scene["duration"]
        
        if not os.path.exists(image_path):
            print(f"      [ERROR] Image not found: {image_path}", file=sys.stderr)
            continue
            
        # Create base clip with Ken Burns zoom effect
        base_clip = create_ken_burns_clip(image_path, duration, size)
        
        # If we have a second image, create a smooth crossfade transition in the middle
        if image_path_2 and os.path.exists(image_path_2) and image_path_2 != image_path:
            clip1 = create_ken_burns_clip(image_path, duration / 2, size)
            clip2 = create_ken_burns_clip(image_path_2, duration / 2, size)
            
            # Crossfade between the two images
            final_scene_clip = concatenate_videoclips([
                clip1.fadeout(0.5),
                clip2.fadein(0.5).set_start((duration / 2) - 0.5)
            ], method="compose").set_duration(duration)
        else:
            final_scene_clip = base_clip
            
        # Add subtle fade in/out for the whole scene to prevent harsh cuts
        final_scene_clip = final_scene_clip.fadein(0.2).fadeout(0.2)
        clips.append(final_scene_clip)
        
        # Add audio
        if os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            # Smooth audio fade in/out to prevent popping
            audio_clip = audio_clip.volumex(1.0).audio_fadein(0.2).audio_fadeout(0.2)
            audio_clips.append(audio_clip)
            
    if not clips:
        print("      [ERROR] No valid clips to assemble", file=sys.stderr)
        sys.exit(1)
        
    print("      Concatenating scenes with smooth transitions...")
    
    # Concatenate all video clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Combine all audio clips
    if audio_clips:
        final_audio = concatenate_videoclips(audio_clips, method="compose") # Note: concatenate_audioclips is deprecated in newer moviepy, use concatenate_videoclips on audio or just sum them
        from moviepy.editor import concatenate_audioclips
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.set_audio(final_audio)
        
    # Write final video
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
    
    print("      ✓ Video assembled successfully with smooth transitions!")
    
    # Cleanup
    final_video.close()
    for clip in clips:
        clip.close()

if __name__ == "__main__":
    print("Video builder with Ken Burns transitions loaded successfully.")
