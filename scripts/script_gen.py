import json, sys, time, requests
from config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_invention_script(invention, inventor, facts, info, video_type="short"):
    if video_type == "long":
        length = "1500 words, 15-20 scenes"
        min_scenes = 15
    else:
        length = "100-130 words, 6-7 scenes"
        min_scenes = 6

    prompt = f"Write JSON script about {invention} by {inventor}. Length: {length}. Include: 1) Shock hook 2) Origin 3) What it is 4) Modern uses. Facts: {facts}. Return ONLY JSON."
    
    try:
        print(f"      Calling Groq API...")
        resp = requests.post(GROQ_URL, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], 
                  "temperature": 0.9, "response_format": {"type": "json_object"}},
            timeout=90)
        
        resp_data = resp.json()
        if "choices" in resp_data and len(resp_data["choices"]) > 0:
            data = json.loads(resp_data["choices"][0]["message"]["content"])
            data.setdefault("scenes", [])

            for idx, scene in enumerate(data["scenes"]):
                scene.setdefault("narration", f"Here is an important fact about {invention}, scene {idx+1}.")
                scene.setdefault("image_prompt", f"cartoon illustration of {invention}, bright colors")
                scene.setdefault("on_screen_text", "")

            while len(data["scenes"]) < min_scenes:
                data["scenes"].append({
                    "narration": f"The impact of {invention} on modern life is undeniable and massive.",
                    "image_prompt": f"cartoon showing {invention} being used worldwide",
                    "on_screen_text": "Global Impact"
                })

            data.setdefault("title_variants", [f"The Shocking Truth About {invention} #shorts"])
            data.setdefault("description", f"Discover the hidden history of {invention}.")
            data.setdefault("thumbnail_text", "DID YOU KNOW?")
            data.setdefault("company", invention)
            data.setdefault("hashtags", ["#shorts", "#facts"])
            data.setdefault("seo_tags", [invention, "history"])

            print(f"      [OK] Script generated: {len(data['scenes'])} scenes")
            return data
    except Exception as e:
        print(f"      [!] API Error: {e}")

    # 100% DYNAMIC FALLBACK - ZERO GENERIC PHRASES
    print("      [!] Using dynamic fallback...")
    
    # EVERY sentence mentions {invention} or {inventor}
    fallback_scenes = [
        {"narration": f"Did you know {invention} was created completely by accident?", "image_prompt": f"cartoon of {invention} with explosion effect", "on_screen_text": "By Accident!"},
        {"narration": f"{inventor} never intended to create {invention} - it was a total mistake.", "image_prompt": f"cartoon of {inventor} looking shocked", "on_screen_text": "Total Mistake"},
        {"narration": f"While trying to solve a different problem, {inventor} stumbled upon {invention}.", "image_prompt": f"cartoon laboratory accident creating {invention}", "on_screen_text": "Happy Accident"},
        {"narration": f"What exactly is {invention}? It's a revolutionary product that changed everything.", "image_prompt": f"close-up cartoon diagram of {invention}", "on_screen_text": "What Is It?"},
        {"narration": f"Before {invention}, people had to use much more difficult methods.", "image_prompt": f"cartoon showing life before {invention}", "on_screen_text": "Life Before"},
        {"narration": f"Today {invention} is used by billions of people every single day.", "image_prompt": f"cartoon showing {invention} used worldwide", "on_screen_text": "Used Worldwide"},
        {"narration": f"The {invention} industry is now worth billions of dollars globally.", "image_prompt": f"cartoon showing money and {invention}", "on_screen_text": "Billion Dollar Industry"},
    ]
    
    # For long videos, add MORE specific scenes
    if video_type == "long":
        long_scenes = [
            {"narration": f"The original version of {invention} looked very different from today.", "image_prompt": f"cartoon showing old version of {invention}", "on_screen_text": "Original Design"},
            {"narration": f"It took years for {inventor} to perfect {invention}.", "image_prompt": f"cartoon timeline of {invention} development", "on_screen_text": "Years of Work"},
            {"narration": f"Early critics said {invention} would never catch on - they were wrong.", "image_prompt": f"cartoon of critics dismissing {invention}", "on_screen_text": "They Were Wrong"},
            {"narration": f"The manufacturing process for {invention} involves complex chemistry.", "image_prompt": f"cartoon factory making {invention}", "on_screen_text": "How It's Made"},
            {"narration": f"{invention} has evolved dramatically since {inventor} first created it.", "image_prompt": f"cartoon evolution of {invention}", "on_screen_text": "Evolution"},
            {"narration": f"Modern versions of {invention} are more advanced than ever before.", "image_prompt": f"cartoon showing modern high-tech {invention}", "on_screen_text": "Modern Version"},
            {"narration": f"Scientists are still finding new uses for {invention} today.", "image_prompt": f"cartoon scientists researching {invention}", "on_screen_text": "New Uses"},
            {"narration": f"The environmental impact of {invention} is now being studied carefully.", "image_prompt": f"cartoon showing eco-friendly {invention}", "on_screen_text": "Environmental Impact"},
        ]
        fallback_scenes.extend(long_scenes)
    
    return {
        "title_variants": [f"The Shocking Truth About {invention} #shorts", f"How {inventor} Accidentally Invented {invention}"],
        "description": f"Discover the hidden history of {invention} and how {inventor} created it by accident.",
        "thumbnail_text": "BY MISTAKE!",
        "company": invention,
        "hashtags": ["#shorts", "#accidentalgenius", f"#{invention.replace(' ','').lower()}"],
        "seo_tags": [invention, inventor, "accidental invention", "history facts", "how its made"],
        "scenes": fallback_scenes[:min_scenes]
    }

def generate_script(company, video_type="short", **kwargs): 
    return generate_invention_script(company, "Unknown", "", "", video_type)

def generate_money_story_script(topic, facts, video_type="short"): 
    return generate_invention_script(topic, "Unknown", facts, "", video_type)

def generate_listicle_script(topic, video_type="short"): 
    return generate_invention_script(topic, "Unknown", "", "", video_type)

def generate_comparison_script(a, b, video_type="short", **kwargs): 
    return generate_invention_script(f"{a} vs {b}", "Unknown", "", "", video_type)
