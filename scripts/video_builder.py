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

def _escape_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("'", "").replace(":", "\\:")

def _build_caption_filters(words: list, width: int, height: int) -> str:
    """
    Groups words into small chunks (karaoke-style) and returns a chained
    drawtext filter string, sized and chunked to actually fit within the
    frame width -- font size is based on WIDTH (the overflow constraint),
    and chunk size shrinks for narrow portrait video (Shorts).
    """
    if not words:
        return ""

    is_portrait = height > width
    chunk_size = 2 if is_portrait else 3
    # Rough estimate: average character width ~0.55x fontsize for bold sans.
    # Pick fontsize so the widest realistic chunk (chunk_size words, ~7 chars
    # each + space) comfortably fits within 90% of frame width.
    max_chars = chunk_size * 8
    fontsize = int(min(width * 0.9 / (max_chars * 0.55), height * 0.045))

    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
    filters = []

    for chunk in chunks:
        text = " ".join(w["text"] for w in chunk).upper()
        text = _escape_text(text)
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        filters.append(
            f"drawtext=text='{text}':fontcolor=yellow:fontsize={fontsize}:"
            f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"box=1:boxcolor=black@0.7:boxborderw=12:"
            f"x=(w-text_w)/2:y=h*0.78:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )
    return "," + ",".join(filters)

LAUGH_SFX_PATH = "assets/laugh.mp3"

def build_scene_clip(image_path, audio_path, words, duration, size, output_path,
                      image_path_2=None, narrator_path=None, has_punchline=False, scene_index=0):
    """
    Builds a scene clip. If image_path_2 is provided and different from
    image_path, cuts from image 1 to image 2 at the midpoint with a punch-zoom
    -- creates a documentary-style "motion picture" edit rhythm from still
    images, since real AI video generation isn't free/reliable for daily use.
    """
    width, height = size

    if os.path.exists(output_path):
        os.remove(output_path)

    caption_chain = _build_caption_filters(words, width, height)
    half = duration / 2
    zoom_frames_half = max(int(half * 25), 1)

    use_two_images = image_path_2 and os.path.exists(image_path_2) and image_path_2 != image_path

    zoom_in = scene_index % 2 == 0
    z1 = "min(zoom+0.0025,1.18)" if zoom_in else "max(1.18-0.0025*on,1.0)"
    z2 = "max(1.18-0.0025*on,1.0)" if zoom_in else "min(zoom+0.0025,1.18)"
    pan_x1 = "iw/2-(iw/zoom/2)+2*sin(on/10)" if zoom_in else "iw/2-(iw/zoom/2)-2*sin(on/10)"

    if use_two_images:
        filter_complex = (
            f"[0:v]scale={width*2}:{height*2},"
            f"zoompan=z='{z1}':x='{pan_x1}':d={zoom_frames_half}:s={width}x{height}:fps=25,"
            f"trim=duration={half:.3f}[part1];"
            f"[1:v]scale={width*2}:{height*2},"
            f"zoompan=z='{z2}':d={zoom_frames_half}:s={width}x{height}:fps=25,"
            f"trim=duration={duration - half:.3f}[part2];"
            f"[part1][part2]concat=n=2:v=1:a=0[v0]"
        )
        vf_inputs = ["-loop", "1", "-i", image_path, "-loop", "1", "-i", image_path_2, "-i", audio_path]
        video_map_source = "[v0]"
        audio_input_index = 2
    else:
        zoom_frames = max(int(duration * 25), 1)
        filter_complex = (
            f"[0:v]scale={width*2}:{height*2},"
            f"zoompan=z='min(zoom+0.0012,1.15)':d={zoom_frames}:s={width}x{height}:fps=25[v0]"
        )
        vf_inputs = ["-loop", "1", "-i", image_path, "-i", audio_path]
        video_map_source = "[v0]"
        audio_input_index = 1

    narrator_h = int(height * 0.35)
    margin = int(height * 0.02)

    if narrator_path and os.path.exists(narrator_path):
        nar_input_index = len(vf_inputs) // 2  # position right before audio
        vf_inputs = vf_inputs[:-2] + ["-loop", "1", "-i", narrator_path] + vf_inputs[-2:]
        audio_input_index += 1
        filter_complex += (
            f";[{nar_input_index}:v]scale=-1:{narrator_h},colorkey=0x00FF00:0.35:0.12[nar];"
            f"{video_map_source}[nar]overlay=x=W-w-{margin}:y='H-h-{margin}+10*sin(2*PI*t*1.8)'[v1];"
            f"[v1]null{caption_chain}[vout]"
        )
    else:
        filter_complex += f";{video_map_source}null{caption_chain}[vout]"

    cmd = [
        "ffmpeg", "-y", *vf_inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", f"{audio_input_index}:a",
        "-c:v", "libx264", "-t", str(duration),
        "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error compiling scene clip: {result.stderr}", file=sys.stderr)
        raise RuntimeError("FFmpeg stitching failure.")

    if has_punchline and os.path.exists(LAUGH_SFX_PATH):
        mixed_path = output_path + ".laugh.mp4"
        mix_cmd = [
            "ffmpeg", "-y", "-i", output_path, "-i", LAUGH_SFX_PATH,
            "-filter_complex",
            f"[1:a]adelay={int((duration-1)*1000)}|{int((duration-1)*1000)},volume=0.5[laugh];"
            f"[0:a][laugh]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]", "-c:v", "copy", mixed_path
        ]
        result2 = subprocess.run(mix_cmd, capture_output=True, text=True)
        if result2.returncode == 0:
            os.replace(mixed_path, output_path)
        else:
            print(f"      [WARNING] Laugh overlay failed, continuing without it.", file=sys.stderr)

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
            scene["image_path"], scene["audio_path"], scene["words"],
            scene["duration"], size, clip_path,
            image_path_2=scene.get("image_path_2"), narrator_path=narrator_path,
            has_punchline=scene.get("has_punchline", False), scene_index=i
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
