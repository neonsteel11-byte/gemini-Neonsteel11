import json, sys, time, requests
from config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_invention_script(invention, inventor, facts, info, video_type="short"):
    length = "1000 words, 12-15 scenes" if video_type == "long" else "100-130 words, 6-7 scenes"
    prompt = f"Write educational script about {invention}. Length: {length}. Include: 1) Shock hook 2) Origin 3) What it is 4) Modern uses. Facts: {facts}"
    
    try:
        resp = requests.post(GROQ_URL, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], 
                  "temperature": 0.9, "response_format": {"type": "json_object"}},
            timeout=60)
        
        # SAFE CHECK: Prevents the 'KeyError' crash
        resp_data = resp.json()
        if "choices" in resp_data and len(resp_data["choices"]) > 0:
            data = json.loads(resp_data["choices"][0]["message"]["content"])
            
            # Ensure minimum scenes
            min_scenes = 12 if video_type == "long" else 6
            while len(data.get("scenes", [])) < min_scenes:
                data["scenes"].append({
                    "narration": "Today millions use this invention daily in homes and workplaces worldwide.",
                    "image_prompt": "modern people using invention, cartoon style, bright colors",
                    "on_screen_text": "Used worldwide"
                })
            return data
    except Exception as e:
        print(f"API Error: {e}")

    # FALLBACK: If API fails, return a safe default script so the video still builds
    print("Using fallback script")
    min_scenes = 12 if video_type == "long" else 6
    return {
        "title_variants": [f"The Truth About {invention} #shorts"],
        "description": "Educational video about accidental genius",
        "thumbnail_text": "DID YOU KNOW?",
        "company": invention,
        "hashtags": ["#shorts", "#facts", "#education"],
        "seo_tags": ["facts", "history"],
        "scenes": [{"narration": f"Let's explore the fascinating story of {invention}.", "image_prompt": "cartoon scene", "on_screen_text": "Facts"} for _ in range(min_scenes)]
    }

def generate_script(company, video_type="short", **kwargs): return generate_invention_script(company, "Unknown", "", "", video_type)
def generate_money_story_script(topic, facts, video_type="short"): return generate_invention_script(topic, "Unknown", facts, "", video_type)
def generate_listicle_script(topic, video_type="short"): return generate_invention_script(topic, "Unknown", "", "", video_type)
def generate_comparison_script(a, b, video_type="short", **kwargs): return generate_invention_script(f"{a} vs {b}", "Unknown", "", "", video_type)
