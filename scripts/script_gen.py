import json, re, sys, time, requests
from config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_invention_script(invention, inventor, facts, info, video_type="short"):
    # Define length and structure based on video type
    if video_type == "long":
        length = "1000-1200 words total, 12-15 scenes minimum"
        structure = "1) Shocking Hook (2 scenes), 2) Detailed Origin Story & Inventor Background (4 scenes), 3) The Science/Mechanics: What it actually is (3 scenes), 4) Modern Applications & How it's used today (4 scenes), 5) The Ironic Legacy (2 scenes)."
    else:
        length = "100-130 words total, 6-7 scenes minimum"
        structure = "1) Shock hook, 2) Origin story, 3) What it is, 4) How used today."

    prompt = f"Write an educational script about {invention} by {inventor}. LENGTH: {length}. STRUCTURE: {structure}. Facts to include: {facts}. Make it highly engaging, use specific numbers, and explain things simply."
    
    for attempt in range(3):
        try:
            print(f"      Calling Groq API for {video_type} script (attempt {attempt+1}/3)...")
            resp = requests.post(GROQ_URL, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], 
                      "temperature": 0.9, "response_format": {"type": "json_object"}},
                timeout=120) # Longer timeout for long-form
            
            if resp.status_code == 200:
                data = json.loads(resp.json()["choices"][0]["message"]["content"])
                
                # Validate scene count
                min_scenes = 12 if video_type == "long" else 6
                while len(data.get("scenes", [])) < min_scenes:
                    data["scenes"].append({
                        "narration": "Today, this invention is used by millions of people every single day in ways the original inventor never could have imagined.",
                        "image_prompt": "modern people using the invention in everyday life, detailed cartoon style",
                        "on_screen_text": "Used Worldwide"
                    })
                
                print(f"      ✓ Script generated: {len(data['scenes'])} scenes")
                return data
            else:
                print(f"      [!] API error: {resp.status_code}")
                time.sleep(3)
        except Exception as e:
            print(f"      [!] Request failed: {e}")
            time.sleep(3)
    
    # Fallback template
    print("      [WARNING] Using fallback script template")
    scene_count = 12 if video_type == "long" else 6
    return {
        "title_variants": [f"The Surprising Truth About {invention}"],
        "description": f"Discover the hidden history and modern uses of {invention}.",
        "thumbnail_text": "DID YOU KNOW?",
        "company": invention,
        "hashtags": ["#accidentalgenius", "#history", "#education"],
        "seo_tags": [invention, "history", "facts", "how its made"],
        "scenes": [{"narration": f"Let's explore the fascinating story of {invention}.", "image_prompt": "cartoon exploration scene", "on_screen_text": "The Story"} for _ in range(scene_count)]
    }

def generate_script(company, video_type="short", **kwargs):
    return generate_invention_script(company, "Unknown", "", "", video_type)

def generate_money_story_script(topic, facts, video_type="short"):
    return generate_invention_script(topic, "Unknown", facts, "", video_type)

def generate_listicle_script(topic, video_type="short"):
    return generate_invention_script(topic, "Unknown", "", "", video_type)

def generate_comparison_script(a, b, video_type="short", **kwargs):
    return generate_invention_script(f"{a} vs {b}", "Unknown", "", "", video_type)
