"""
Main entry point. Generates one funny-finance video about a company and
(optionally) uploads it to YouTube.

Usage:
  python3 main.py "Tesla" --type short --upload
  python3 main.py "Nvidia" --type long
"""
import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from scripts.script_gen import generate_script
from scripts.tts_gen import generate_voiceover
from scripts.image_gen import generate_image
from scripts.video_builder import build_video
from config import LONGFORM_SIZE, SHORTS_SIZE, OUTPUT_DIR


def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def run(company: str, video_type: str, upload: bool, privacy: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_name = sanitize_filename(company)
    tmp_dir = os.path.join(OUTPUT_DIR, f"tmp_{safe_name}_{video_type}")
    os.makedirs(tmp_dir, exist_ok=True)

    size = SHORTS_SIZE if video_type == "short" else LONGFORM_SIZE

    print(f"[1/4] Generating script for '{company}' ({video_type})...")
    script = generate_script(company, video_type)
    print(f"      Title: {script['title']}")
    print(f"      Scenes: {len(script['scenes'])}")

    print("[2/4] Generating voiceover + images per scene...")
    scene_data = []
    for i, scene in enumerate(script["scenes"]):
        audio_path = os.path.join(tmp_dir, f"audio_{i}.mp3")
        image_path = os.path.join(tmp_dir, f"image_{i}.png")

        print(f"      scene {i+1}/{len(script['scenes'])}: generating voiceover...")
        duration = generate_voiceover(scene["narration"], audio_path)

        print(f"      scene {i+1}/{len(script['scenes'])}: generating image...")
        generate_image(scene["image_prompt"], image_path, size)

        scene_data.append({
            "image_path": image_path,
            "audio_path": audio_path,
            "caption": scene["on_screen_text"],
            "duration": duration,
        })

    print("[3/4] Assembling final video (this checks for black-frame bugs automatically)...")
    final_path = os.path.join(OUTPUT_DIR, f"{safe_name}_{video_type}.mp4")
    build_video(scene_data, size, final_path, tmp_dir)

    print(f"[4/4] Done. Final video: {final_path}")

    if upload:
        from scripts.youtube_upload import upload_video
        description = (
            f"{script['title']}\n\nFunny finance commentary on {company}. "
            f"Not financial advice, just laughs.\n\n#{sanitize_filename(company)} #finance #funny"
        )
        upload_video(
            final_path, script["title"], description,
            tags=[company, "finance", "funny finance", "stocks"],
            is_short=(video_type == "short"),
            privacy_status=privacy,
        )

    # cleanup intermediate scene files, keep final video
    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a funny finance video about a company.")
    parser.add_argument("company", help="Company name, e.g. 'Tesla'")
    parser.add_argument("--type", choices=["long", "short"], default="short")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube after building")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="private",
                         help="Start with 'private' or 'unlisted' until you trust the pipeline")
    args = parser.parse_args()

    run(args.company, args.type, args.upload, args.privacy)
