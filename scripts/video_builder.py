import os, sys
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, concatenate_audioclips


def add_captions_to_clip(clip, words, video_width, video_height, group_size=3):
    """Overlay captions synced to word timings, grouped into short readable phrases."""
    if not words:
        return clip
    is_vertical = video_height > video_width
    fontsize = int(video_height * 0.045) if is_vertical else int(video_height * 0.038)
    clean_words = [w for w in words if w.get("text", "").strip()]
    groups = [clean_words[i:i + group_size] for i in range(0, len(clean_words), group_size)]
    caption_clips = []
    for group in groups:
        text = " ".join(w["text"].strip() for w in group)
        start = group[0].get("start", 0)
        end = group[-1].get("end", start + 0.6)
        try:
            txt = TextClip(text, fontsize=fontsize, color='white', font='Arial-Bold',
                            stroke_color='black', stroke_width=3, method='caption',
                            size=(int(video_width * 0.85), None))
            txt = txt.set_position(('center', 0.78), relative=True)
            txt = txt.set_start(start).set_duration(max(end - start, 0.3))
            caption_clips.append(txt)
        except Exception as e:
            print(f"      [!] Caption render failed for phrase '{text}': {e}", file=sys.stderr)
    if not caption_clips:
        return clip
    return CompositeVideoClip([clip] + caption_clips)


def build_video(scene_data, size, output_path, tmp_dir):
    clips = []
    audio_clips = []
    for scene in scene_data:
        img_path = scene["image_path"]
        aud_path = scene["audio_path"]
        if not os.path.exists(img_path):
            print(f"      [ERROR] Missing: {img_path}", file=sys.stderr)
            continue

        # Derive duration directly from the real audio clip so image and audio
        # can never mismatch and silently truncate dialogue on export.
        if os.path.exists(aud_path):
            aud_clip = AudioFileClip(aud_path)
            dur = aud_clip.duration + 0.15  # small safety buffer
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
        # Guarantee the exported video is never shorter than the full audio track.
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
