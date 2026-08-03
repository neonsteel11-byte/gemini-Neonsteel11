"""
Main entry point for Accidental Genius channel.
Generates videos about accidental inventions with real inventor photos + cartoon storytelling.
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
    content_format = "single_company"
    inventor_image_url = None
    
    if company.startswith("HOWITWORKS:"):
        content_format = "how_it_works"
        topic = company.split(":", 1)[1]
        print(f"      How-it-works mode: {topic}")
        from scripts.script_gen import generate_money_story_script
        from scripts.fetch_wikipedia import fetch_wiki_info
        from scripts.fetch_invention_uses import fetch_invention_details
        topic_info = fetch_wiki_info(topic)
        script = generate_money_story_script(topic, topic_info["summary"], video_type)
        company = topic
        
    elif company.startswith("LISTICLE:"):
        content_format = "listicle"
        topic = company.split(":", 1)[1]
        print(f"      Listicle mode: {topic}")
        from scripts.script_gen import generate_listicle_script
        script = generate_listicle_script(topic, video_type)
        company = topic
        
    elif company.startswith("WIDE:"):
        content_format = "wide_topic"
        topic = company.split(":", 1)[1]
        print(f"      Wide-topic mode: {topic}")
        from scripts.script_gen import generate_money_story_script
        from scripts.fetch_wikipedia import fetch_wiki_info
        from scripts.fetch_invention_uses import fetch_invention_details
        topic_info = fetch_wiki_info(topic)
        script = generate_money_story_script(topic, topic_info["summary"], video_type)
        company = topic
        
    elif company.startswith("MONEY:"):
        content_format = "money_story"
        topic = company.split(":", 1)[1]
        print(f"      Money story mode: {topic}")
        from scripts.script_gen import generate_money_story_script
        from scripts.fetch_wikipedia import fetch_wiki_info
        from scripts.fetch_invention_uses import fetch_invention_details
        topic_info = fetch_wiki_info(topic)
        script = generate_money_story_script(topic, topic_info["summary"], video_type)
        company = topic
        
    elif company.startswith("INVENTION:"):
        content_format = "invention_history"
        _, invention, inventor = company.split(":", 2)
        print(f"      Invention mode: {invention} by {inventor}")
        from scripts.script_gen import generate_invention_script
        from scripts.fetch_wikipedia import fetch_wiki_info
        from scripts.fetch_invention_uses import fetch_invention_details
        
        # Fetch BOTH inventor and invention info
        inventor_info = fetch_wiki_info(inventor)
        invention_info = fetch_wiki_info(invention)
        invention_details = fetch_invention_details(invention)
        
        from scripts.fetch_reddit_facts import fetch_reddit_context
        reddit_snippets = fetch_reddit_context(invention)
        combined_facts = invention_info["summary"] + " Additional angles: " + "; ".join(reddit_snippets)
        
        script = generate_invention_script(
            invention, inventor, inventor_info["summary"], combined_facts, video_type
        )
        
        # CRITICAL: Store inventor's real photo URL for Scene 1
        inventor_image_url = inventor_info.get("image_url")
        if inventor_image_url:
            print(f"      ✓ Found real photo of {inventor}")
        else:
            print(f"      [!] No real photo of {inventor} - will use cartoon portrait")
        
        company = invention
        
    elif "|" in company:
        content_format = "comparison"
        company_a, company_b = [c.strip() for c in company.split("|", 1)]
        print(f"      Comparison mode: {company_a} vs {company_b}")
        from scripts.script_gen import generate_comparison_script
        news_a = fetch_recent_headlines(company_a)
        news_b = fetch_recent_headlines(company_b)
        script = generate_comparison_script(company_a, company_b, video_type, news_a, news_b)
        company = f"{company_a} vs {company_b}"
        
    else:
        print("      Fetching recent real news for grounding...")
        news_headlines = fetch_recent_headlines(company)
        print(f"      Found {len(news_headlines)} real headlines to use.")
        from scripts.fetch_trending import fetch_top_titles
        trending_titles = fetch_top_titles(f"{company} stock")
        if trending_titles:
            print(f"      Trending titles found: {trending_titles[:2]}")
            news_headlines = news_headlines + [f"Popular video title: {t}" for t in trending_titles[:2]]
        import subprocess
        angle = subprocess.run(["python", "scripts/pick_angle.py"], capture_output=True, text=True).stdout.strip()
        print(f"      Story angle: {angle}")
        past_titles = [entry["title_variants"][0] for entry in _load_manifest() if "title_variants" in entry]
        script = generate_script(company, video_type, news_headlines=news_headlines, angle=angle, avoid_titles=past_titles)

    video_seed = random.randint(1, 999999)
    print(f"      Title: {script['title_variants'][0]}")
    print(f"      Visual seed: {video_seed}")
    print(f"      Scenes: {len(script['scenes'])}")

    print("[2/4] Generating voiceover + images per scene...")
    
    scene_data = []
    for i, scene in enumerate(script["scenes"]):
        audio_path = os.path.join(tmp_dir, f"audio_{i}.mp3")
        image_path = os.path.join(tmp_dir, f"image_{i}.png")
        image_path_2 = os.path.join(tmp_dir, f"image_{i}_b.png")
        
        print(f"      scene {i+1}/{len(script['scenes'])}: generating voiceover...")
        duration, words = generate_voiceover(scene["narration"], audio_path)
        print(f"      scene {i+1} audio duration: {duration:.2f}s")
        
        print(f"      scene {i+1}: generating images...")
        
        # SCENE 1 SPECIAL HANDLING:
        # For INVENTION videos: Use inventor's real photo (or cartoon portrait)
        # For other videos: Use cartoon illustrations only
        if i == 0 and content_format == "invention_history":
            if inventor_image_url:
                # Download inventor's real photo
                from scripts.image_gen import download_real_image
                success = download_real_image(inventor_image_url, image_path, size)
                if success:
                    print(f"      ✓ Used real photo of inventor for Scene 1")
                else:
                    # Fallback: Generate cartoon portrait of inventor
                    print(f"      [!] Real photo failed, generating cartoon portrait...")
                    generate_image(f"a respectful cartoon portrait of {inventor}, the inventor", 
                                 image_path, size, seed=video_seed)
                image_path_2 = image_path  # Single image, no second cut
            else:
                # No real photo available - generate cartoon portrait
                generate_image(f"a respectful cartoon portrait of {inventor}, the inventor", 
                             image_path, size, seed=video_seed)
                image_path_2 = image_path
                print(f"      ✓ Generated cartoon portrait of inventor for Scene 1")
        else:
            # All other scenes: Use cartoon illustrations based on script
            generate_image(scene["image_prompt"], image_path, size, seed=video_seed)
            generate_image(scene["image_prompt"], image_path_2, size, seed=video_seed + 1000 + i)
        
        scene_data.append({
            "image_path": image_path,
            "image_path_2": image_path_2,
            "audio_path": audio_path,
            "words": words,
            "duration": duration,
            "has_punchline": scene.get("has_punchline", False),
        })

    print("      Generating subscribe call-to-action scene...")
    cta_audio_path = os.path.join(tmp_dir, "cta_audio.mp3")
    cta_image_path = os.path.join(tmp_dir, "cta_image.png")
    import random as _r
    cta_text = _r.choice([
        "Subscribe to see the accidental side of history you were never taught in school.",
        "If that surprised you, tag a friend who needs to see this.",
        "Send this to someone who won't believe it either."
    ])
    cta_duration, cta_words = generate_voiceover(cta_text, cta_audio_path)
    mascot_asset_path = "assets/lucky_mascot.png"
    if os.path.exists(mascot_asset_path):
        import shutil as _shutil
        from PIL import Image as _Image
        img = _Image.open(mascot_asset_path).convert("RGB").resize(size)
        img.save(cta_image_path)
        print("      Using lucky mascot for CTA scene.")
    else:
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

    print("[3/4] Assembling final video...")
    final_path = os.path.join(OUTPUT_DIR, f"{safe_name}_{video_type}.mp4")
    build_video(scene_data, size, final_path, tmp_dir)
    print(f"[4/4] Done. Final video: {final_path}")

    hashtags_list = script.get("hashtags", [])
    title = script['title_variants'][0]
    tiktok_caption = f"{title} | Accidental Genius\n" + " ".join(hashtags_list[:5]) + " #fyp #foryou #AccidentalGenius"
    instagram_caption = f"{title} | Accidental Genius\n.\n.\n.\n" + " ".join(hashtags_list[:3]) + " #reels #AccidentalGenius"
    facebook_caption = f"{title} | Accidental Genius"
    caption_path = os.path.join(OUTPUT_DIR, f"{safe_name}_{video_type}_captions.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write("=== TIKTOK ===\n" + tiktok_caption + "\n")
        f.write("=== INSTAGRAM ===\n" + instagram_caption + "\n")
        f.write("=== FACEBOOK ===\n" + facebook_caption + "\n")
    print(f"      Platform-specific captions saved: {caption_path}")

    if upload:
        from scripts.youtube_upload import upload_video
        hashtags = " ".join(script.get("hashtags", []))
        body = script.get("description", "").strip()
        if not body:
            body = f"A surprising true story: {company}."
        brand_line = "Accidental Genius -- the wild stories behind history's most brilliant mistakes."
        description = f"{script['title_variants'][0]}\n{body}\n{brand_line}\n{hashtags} #AccidentalGenius"
        video_id = upload_video(
            final_path, script["title_variants"][0], description,
            tags=script.get("seo_tags", []) + [company, "finance", "cartoon"],
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
            "content_format": content_format,
        })
        _save_manifest(manifest)
        print(f"      Logged to {MANIFEST_PATH} for performance tracking.")

    shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Accidental Genius video")
    parser.add_argument("company", help="Company name or INVENTION:Invention:Inventor")
    parser.add_argument("--type", choices=["long", "short"], default="short")
    parser.add_argument("--upload", action="store_true", help="Upload to YouTube")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="private")
    args = parser.parse_args()
    run(args.company, args.type, args.upload, args.privacy)
