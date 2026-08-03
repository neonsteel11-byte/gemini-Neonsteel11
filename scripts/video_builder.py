"""
Builds the final video with SLIDING TRANSITIONS between images.
Uses MoviePy for professional video assembly with smooth effects.
"""
import os
import sys
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips,
    ColorClip, fadein, fadeout
)
from PIL import Image

def create_sliding_transition(clip1, clip2, duration=0.5):
    """
    Create a smooth sliding transition between two clips.
    Clip2 slides in from the right, replacing clip1.
    """
    from moviepy.editor import CompositeVideoClip
    
    # Create transition clip
    def make_frame(t):
        if t < duration:
            # During transition: clip2 slides in from right
            progress = t / duration
            offset = int(clip2.w * (1 - progress))
            
            # Composite: clip1 on left, clip2 sliding in from right
            composite = CompositeVideoClip([
                clip1.set_position((0, 0)),
                clip2.set_position((offset, 0))
            ])
            return composite.get_frame(t)
        else:
            # After transition: just clip2
            return clip2.get_frame(t - duration)
    
    from moviepy.editor import VideoClip
    transition_clip = VideoClip(make_frame, duration=duration + clip2.duration)
    return transition_clip

def build_video(scene_data: list, size: tuple, output_path: str, tmp_dir: str):
    """
    Builds final video with:
    - Sliding transitions between scenes
    - Smooth fade in/out for audio
    - Professional assembly
    """
    clips = []
    audio_clips = []
    
    print(f"      Building video with {len(scene_data)} scenes...")
    
    for i, scene in enumerate(scene_data):
        image_path = scene["image_path"]
        image_path_2 = scene.get("image_path_2")
        audio_path = scene["audio_path"]
        duration = scene["duration"]
        
        if not os.path.exists(image_path):
            print(f"      [ERROR] Image not found: {image_path}", file=sys.stderr)
            continue
        
        # Create image clip
        img_clip = ImageClip(image_path, duration=duration).resize(size)
        
        # Add second image for motion cut (if available)
        if image_path_2 and os.path.exists(image_path_2) and image_path_2 != image_path:
            img_clip_2 = ImageClip(image_path_2, duration=duration/2).resize(size)
            
            # Create sliding transition between the two images
            transition = create_sliding_transition(img_clip, img_clip_2, duration=0.3)
            img_clip = transition.set_duration(duration)
        
        # Add fade in/out for smoothness
        img_clip = img_clip.fadein(0.2).fadeout(0.2)
        clips.append(img_clip)
        
        # Add audio
        if os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            audio_clip = audio_clip.volumex(1.0)  # Normalize volume
            audio_clips.append(audio_clip)
    
    if not clips:
        print("      [ERROR] No valid clips to assemble", file=sys.stderr)
        sys.exit(1)
    
    print("      Concatenating clips with transitions...")
    
    # Concatenate all clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Combine audio
    if audio_clips:
        from moviepy.editor import concatenate_audioclips
        final_audio = concatenate_audioclips(audio_clips)
        final_video = final_video.set_audio(final_audio)
    
    # Add final fade out
    final_video = final_video.fadeout(0.5)
    
    # Write final video
    print(f"      Writing final video to: {output_path}")
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
    
    print(f"      ✓ Video assembled successfully: {output_path}")
    
    # Cleanup temp files
    for clip in clips:
        clip.close()
    final_video.close()

if __name__ == "__main__":
    # Test
    print("Video builder with sliding transitions loaded successfully")
