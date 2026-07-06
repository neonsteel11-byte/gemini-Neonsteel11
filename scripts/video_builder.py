import os
import subprocess
import sys

def _check_ffmpeg():
    """Verifies if ffmpeg is available in the system path."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def build_scene_clip(image_path, audio_path, caption, duration, size, output_path):
    """Stitches a single image and audio file into an intermediate video clip using ffmpeg."""
    width, height = size
    
    # Clean up old existing clips
    if os.path.exists(output_path):
        os.remove(output_path)

    # Clean text to prevent bash breaking
    safe_caption = caption.replace("'", "").replace('"', "")

    # Direct ffmpeg call: pairs image + audio, scales to required size, burns simple text drawtext overlay
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264", "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={width}:{height},drawtext=text='{safe_caption}':fontcolor=white:fontsize=40:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=h-150",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error compiling scene clip: {result.stderr}", file=sys.stderr)
        raise RuntimeError("FFmpeg stitching failure.")

def build_video(scene_data, size, final_output_path, tmp_dir):
    """Combines all scene clips into a final master video."""
    print("      Verifying environment core requirements...")
    
    if not _check_ffmpeg():
        print("\n⚠️  [ENVIRONMENT NOTICE] ffmpeg was not found on your local machine.")
        print("💡 Skipping local video assembly rendering safely. Your generated assets are preserved.")
        print("🚀 Push this commit to GitHub, and the cloud workflow will render your complete video automatically!\n")
        return

    clip_paths = []
    # 1. Compile individual scene segments
    for i, scene in enumerate(scene_data):
        clip_path = os.path.join(tmp_dir, f"scene_clip_{i}.mp4")
        print(f"      Compiling Cloud Asset Layer [Scene {i+1}/{len(scene_data)}]...")
        build_scene_clip(
            scene["image_path"], scene["audio_path"], scene["caption"],
            scene["duration"], size, clip_path
        )
        clip_paths.append(clip_path)

    # 2. Generate a concatenation list file for ffmpeg
    concat_file_path = os.path.join(tmp_dir, "concat_list.txt")
    with open(concat_file_path, "w") as f:
        for path in clip_paths:
            # Format absolute paths correctly for ffmpeg concat
            normalized_path = os.path.abspath(path).replace("\\", "/")
            f.write(f"file '{normalized_path}'\n")

    # 3. Concatenate all clips into the final video file
    print("      Stitching video tracks into final production file...")
    if os.path.exists(final_output_path):
        os.remove(final_output_path)

    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file_path, "-c", "copy", final_output_path
    ]
    
    result = subprocess.run(concat_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error concatenating master video: {result.stderr}", file=sys.stderr)
        raise RuntimeError("FFmpeg master concatenation failure.")
    
    print(f"✅ Production complete! Master File: {final_output_path}")
