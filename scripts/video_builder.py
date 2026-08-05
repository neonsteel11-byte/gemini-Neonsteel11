import os, sys
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips

def build_video(scene_data, size, output_path, tmp_dir):
    clips = []
    audio_clips = []
    
    for scene in scene_data:
        img_path = scene["image_path"]
        aud_path = scene["audio_path"]
        dur = scene["duration"]
        
        if not os.path.exists(img_path):
            print(f"      [ERROR] Missing: {img_path}", file=sys.stderr)
            continue
        
        clip = ImageClip(img_path).set_duration(dur).fadein(0.3).fadeout(0.3)
        clips.append(clip)
        
        if os.path.exists(aud_path):
            audio_clips.append(AudioFileClip(aud_path))
    
    if not clips:
        sys.exit(1)
    
    video = concatenate_videoclips(clips, method="compose")
    if audio_clips:
        video = video.set_audio(concatenate_audioclips(audio_clips))
    
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac',
                         temp_audiofile='temp.m4a', remove_temp=True, verbose=False, logger=None)
    video.close()
