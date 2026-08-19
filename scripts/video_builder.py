import os, sys
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, concatenate_audioclips


def add_captions_to_clip(clip, words, video_width, video_height):
    """Overlay the full narration as one readable caption for the whole scene,
    so it always reads as a complete line/sentence instead of fragments."""
    if not words:
        return clip
    is_vertical = video_height > video_width
    fontsize = int(video_height * 0.04) if is_vertical else int(video_height * 0.034)
    full_text = " ".join(w.get("text", "").strip() for w in words if w.get("text", "").strip())
    if not full_text:
        return clip
    try:
        txt = TextClip(full_text, fontsize=fontsize, color='white', font='Arial-Bold',
                        stroke_color='black', stroke_width=3, method='caption',
                        size=(int(video_width * 0.85), None))
        txt = txt.set_position(('center', 0.78), relative=True)
        txt = txt.set_start(0).set_duration(clip.duration)
        return CompositeVideoClip([clip, txt])
    except Exception as e:
        print(f"      [!] Caption render failed: {e}", file=sys.stderr)
        return clip


def build_video(scene_data, size, output_path, tmp_dir):
    clips = []
    audio_clips = []
    for scene in scene_data:
        img_path = scene["image_path"]
        aud_path = scene["audio_path"]
        if not os.path.exists(img_path):
            print(f"      [ERROR] Missing: {img_path}", file=sys.stderr)
            continue

        if os.path.exists(aud_path):
            aud_clip = AudioFileClip(aud_path)
            dur = aud_clip.duration + 0.15
            audio_clips.append(aud_clip)
        else:
            dur = scene.get("duration", 3.0)

        clip = ImageClip(img_path).set_duration(dur).fadein(0.3).fadeout(0.3)
        words = scene.get("words", [])
        clip = add_captions_to_clip(clip, words, size[0], size[1])
        clips.append(clip)

    if not clips:
        sys.exit(1)

    video = concatenate_videoclips(clips, method="compose")
    if audio_clips:
        combined_audio = concatenate_audioclips(audio_clips)
        video = video.set_audio(combined_audio)
        if combined_audio.duration > video.duration:
            video = video.set_duration(combined_audio.duration)

    print(f"      Expected final duration before render: {video.duration:.2f}s")
    video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac',
                         temp_audiofile='temp.m4a', remove_temp=True, verbose=False, logger=None)
    video.close()

    try:
        import subprocess
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", output_path],
            capture_output=True, text=True
        )
        actual_duration = result.stdout.strip()
        print(f"      [CHECK] Actual rendered file duration (ffprobe): {actual_duration}s")
    except Exception as e:
        print(f"      [!] Could not verify rendered duration: {e}")
