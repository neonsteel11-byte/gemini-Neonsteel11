"""
Main entry point. Generates one funny-finance cartoon video about a company
and (optionally) uploads it to YouTube, logging it to a manifest for later
performance-based title/description optimization.
"""
import argparse
import json
import os
import random
import shutil
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from scripts.script_gen import generate_script
from scripts.tts_gen import generate_voiceover
from scripts.image_gen import generate_image
from scripts.video_builder import build_video
from config import LONGFORM_SIZE, SHORTS_SIZE, OUTPUT_DIR

MANIFEST_PATH = "video_manifest.json"


def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def _load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def run(company: str, video_type: str, upload: bool, privacy: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_name = sanitize_filename(company)
    tmp_dir = os.path.join(OUTPUT_DIR, f"tmp_{safe_name}_{video_type}")
    os.makedirs(tmp_dir, exist_ok=True)

    size = SHORTS_SIZE if video_type == "short" else LONGFORM_SIZE

    print(f"[1/4] Generating script for '{company}' ({video_type})...")
    from scripts.fetch_news import fetch_recent_headlines
    print("      Fetching recent real news for grounding...")
    news_headlines = fetch_recent_headlines(company)
    print(f"      Found {len(news_headlines)} real headlines to use.")
    script = generate_script(company, video_type, news_headlines=news_headlines)
    video_seed = random.randint(1, 999999)
    print(f"      Title: {script['title_variants'][0]}")
    print(f"      Visual seed for consistency: {video_seed}")
    print(f"      Scenes: {len(script['scenes'])}")

    print("[2/4] Generating voiceover + images per scene...")
    narrator_path = os.path.join(tmp_dir, "narrator.png")
    from scripts.image_gen import generate_narrator
    print("      Generating recurring narrator character...")
    generate_narrator(narrator_path)

    scene_data = []
    for i, scene in enumerate(script["scenes"]):
        audio_path = os.path.join(tmp_dir, f"audio_{i}.mp3")
        image_path = os.path.join(tmp_dir, f"image_{i}.png")

        print(f"      scene {i+1}/{len(script['scenes'])}: generating voiceover...")
        duration, words = generate_voiceover(scene["narration"], audio_path)
        print(f"      scene {i+1} audio duration: {duration:.2f}s")

        print(f"      scene {i+1}/{len(script['scenes'])}: generating image...")
        generate_image(scene["image_prompt"], image_path, size, seed=video_seed)

        scene_data.append({
            "image_path": image_path,
            "audio_path": audio_path,
            "words": words,
            "duration": duration,
        })

    print("      Generating subscribe call-to-action scene...")
    cta_audio_path = os.path.join(tmp_dir, "cta_audio.mp3")
    cta_image_path = os.path.join(tmp_dir, "cta_image.png")
    cta_duration, cta_words = generate_voiceover(
        "If that made you laugh, hit subscribe -- new funny finance videos every day!",
        cta_audio_path
    )
    generate_image(
        "a cheerful cartoon character giving a thumbs up next to a giant bell icon, "
        "flat vector cartoon illustration, bold outlines, bright colors",
        cta_image_path, size
    )
    scene_data.append({
        "image_path": cta_image_path,
        "audio_path": cta_audio_path,
        "words": cta_words,
        "duration": cta_duration,
    })

    print("[3/4] Assembling final video (this checks for black-frame/audio bugs automatically)...")
    final_path = os.path.join(OUTPUT_DIR, f"{safe_name}_{video_type}.mp4")
    build_video(scene_data, size, final_path, tmp_dir, narrator_path=narrator_path)

    print(f"[4/4] Done. Final video: {final_path}")

    if upload:
        from scripts.youtube_upload import upload_video
        hashtags = " ".join(script.get("hashtags", []))
        description = (
            f"{script['title_variants'][0]}\n\n"
            f"Funny finance commentary on {company}. Satire, not financial advice.\n\n"
            f"{hashtags}"
        )
        video_id = upload_video(
            final_path, script["title_variants"][0], description,
            tags=[company, "finance", "funny finance", "stocks", "cartoon"],
            is_short=(video_type == "short"),
            privacy_status=privacy,
        )

        manifest = _load_manifest()
        manifest.append({
            "video_id": video_id,
            "company": company,
            "video_type": video_type,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "title_variants": script["title_variants"],
            "hashtags": script.get("hashtags", []),
            "variant_index": 0,
            "optimized": False,
            "privacy": privacy,
            "auto_published": False,
        })
        _save_manifest(manifest)
        print(f"      Logged to {MANIFEST_PATH} for performance tracking.")

    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a funny finance cartoon video about a company.")
    parser.add_argument("company", help="Company name, e.g. 'Tesla'")
    parser.add_argument("--type", choices=["long", "short"], default="short")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube after building")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="private")
    args = parser.parse_args()

    run(args.company, args.type, args.upload, args.privacy)
