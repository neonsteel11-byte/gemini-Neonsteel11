import os, sys
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, concatenate_audioclips

def add_captions_to_clip(clip, words, video_width, video_height):
    """Overlay karaoke-style captions synced to word timings."""
    if not words:
        return clip
    is_vertical = video_height > video_width
    fontsize = int(video_height * 0.055) if is_vertical else int(video_height * 0.045)
    caption_clips = []
    for w in words:
        text = w.get("text", "").strip()
        if not text:
            continue
        start = w.get("start", 0)
        end = w.get("end", start + 0.3)
        try:
            txt = TextClip(text, fontsize=fontsize, color='white', font='Arial-Bold',
                            stroke_color='black', stroke_width=3)
            txt = txt.set_position(('center', 0.78), relative=True)
            txt = txt.set_start(start).set_duration(max(end - start, 0.15))
            caption_clips.append(txt)
        except Exception as e:
            print(f"      [!] Caption render failed for word '{text}': {e}", file=sys.stderr)
    if not caption_clips:
        return clip
    return CompositeVideoClip([clip] + caption_clips)

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
        words = scene.get("words", [])
        clip = add_captions_to_clip(clip, words, size[0], size[1])
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
