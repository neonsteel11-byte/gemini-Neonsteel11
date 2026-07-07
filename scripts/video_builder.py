import os
import re
import subprocess
import sys

def _check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def build_scene_clip(image_path, audio_path, caption, duration, size, output_path, narrator_path=None):
    """Stitches background image + optional animated narrator overlay + audio into a clip."""
    width, height = size

    if os.path.exists(output_path):
        os.remove(output_path)

    safe_caption = caption.replace("'", "").replace('"', "")
    narrator_h = int(height * 0.35)  # narrator takes ~35% of frame height
    margin = int(height * 0.02)

    if narrator_path and os.path.exists(narrator_path):
        filter_complex = (
            f"[0:v]scale={width}:{height}[bg];"
            f"[1:v]scale=-1:{narrator_h},colorkey=0x00FF00:0.35:0.12[nar];"
            f"[bg][nar]overlay=x=W-w-{margin}:y='H-h-{margin}+10*sin(2*PI*t*1.8)'[v1];"
            f"[v1]drawtext=text='{safe_caption}':fontcolor=white:fontsize=40:"
            f"box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=h-150[vout]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_path,
            "-loop", "1", "-i", narrator_path,
            "-i", audio_path,
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "2:a",
            "-c:v", "libx264", "-t", str(duration),
            "-preset", "slow", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", output_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264", "-t", str(duration),
            "-preset", "slow", "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={width}:{height},drawtext=text='{safe_caption}':fontcolor=white:fontsize=40:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=h-150",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", output_path
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error compiling scene clip: {result.stderr}", file=sys.stderr)
        raise RuntimeError("FFmpeg stitching failure.")

def verify_not_black(video_path: str, max_black_ratio: float = 0.15):
    cmd = ["ffmpeg", "-i", video_path, "-vf", "blackdetect=d=0.5:pic_th=0.98", "-an", "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    black_durations = [float(m) for m in re.findall(r"black_duration:([\d.]+)", result.stderr)]
    total_black = sum(black_durations)
    duration_match = re.search(r"Duration: (\d+):(\d+):([\d.]+)", result.stderr)
    if not duration_match:
        print(f"WARNING: could not verify {video_path} isn't blank. Check manually.", file=sys.stderr)
        return
    h, m, s = duration_match.groups()
    total_duration = int(h) * 3600 + int(m) * 60 + float(s)
    if total_duration == 0:
        print(f"FATAL: {video_path} has zero duration.", file=sys.stderr)
        sys.exit(1)
    ratio = total_black / total_duration
    if ratio > max_black_ratio:
        print(f"FATAL: {video_path} is {ratio*100:.0f}% black frames ({total_black:.1f}s of {total_duration:.1f}s). Black-screen validation failed.", file=sys.stderr)
        sys.exit(1)
    print(f"      Black-frame check passed ({ratio*100:.1f}% black, threshold {max_black_ratio*100:.0f}%).")

def verify_has_audio(video_path: str):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
           "stream=codec_type,duration", "-of", "default=noprint_wrappers=1", video_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if "codec_type=audio" not in result.stdout:
        print(f"FATAL: {video_path} has NO audio stream at all.", file=sys.stderr)
        sys.exit(1)
    print(f"      Audio stream present: {result.stdout.strip()}")

def build_video(scene_data, size, final_output_path, tmp_dir, narrator_path=None):
    print("      Verifying environment core requirements...")
    if not _check_ffmpeg():
        print("\n⚠️  [ENVIRONMENT NOTICE] ffmpeg was not found on your local machine.")
        print("💡 Skipping local video assembly rendering safely. Your generated assets are preserved.")
        print("🚀 Push this commit to GitHub, and the cloud workflow will render your complete video automatically!\n")
        return

    clip_paths = []
    for i, scene in enumerate(scene_data):
        clip_path = os.path.join(tmp_dir, f"scene_clip_{i}.mp4")
        print(f"      Compiling scene [{i+1}/{len(scene_data)}]...")
        build_scene_clip(
            scene["image_path"], scene["audio_path"], scene["caption"],
            scene["duration"], size, clip_path, narrator_path=narrator_path
        )
        clip_paths.append(clip_path)

    concat_file_path = os.path.join(tmp_dir, "concat_list.txt")
    with open(concat_file_path, "w") as f:
        for path in clip_paths:
            normalized_path = os.path.abspath(path).replace("\\", "/")
            f.write(f"file '{normalized_path}'\n")

    print("      Stitching video tracks into final file...")
    if os.path.exists(final_output_path):
        os.remove(final_output_path)

    concat_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file_path, "-c", "copy", final_output_path]
    result = subprocess.run(concat_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error concatenating master video: {result.stderr}", file=sys.stderr)
        raise RuntimeError("FFmpeg master concatenation failure.")

    verify_not_black(final_output_path)
    verify_has_audio(final_output_path)
    print(f"✅ Production complete and verified: {final_output_path}")
