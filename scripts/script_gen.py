import json, re, sys, requests
from config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

PROMPT = """Write educational script about accidental inventions.
MANDATORY: 100-130 words minimum, 6-7 scenes.
STRUCTURE: 1) Shock hook 2) Accident story 3) What it IS 4) How used today
Return JSON with scenes array."""

def generate_invention_script(invention, inventor, facts, info, video_type="short"):
    length = "100-130 words, 6-7 scenes" if video_type=="short" else "1000 words"
    prompt = f"Write about {invention} by {inventor}. {length}. Facts: {facts}. MUST include what it is and how used today."
    
    resp = requests.post(GROQ_URL, 
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], 
              "temperature": 0.9, "response_format": {"type": "json_object"}},
        timeout=60)
    
    data = json.loads(resp.json()["choices"][0]["message"]["content"])
    
    # Ensure minimum 6 scenes
    while len(data.get("scenes", [])) < 6:
        data["scenes"].append({
            "narration": "Today millions use this invention daily in homes, schools, and workplaces worldwide.",
            "image_prompt": "modern people using invention, cartoon",
            "on_screen_text": "Used worldwide"
        })
    
    return data

def generate_script(company, video_type="short", **kwargs):
    return generate_invention_script(company, "Unknown", "", "", video_type)

def generate_money_story_script(topic, facts, video_type="short"):
    return generate_invention_script(topic, "Unknown", facts, "", video_type)

def generate_listicle_script(topic, video_type="short"):
    return generate_invention_script(topic, "Unknown", "", "", video_type)

def generate_comparison_script(a, b, video_type="short", **kwargs):
    return generate_invention_script(f"{a} vs {b}", "Unknown", "", "", video_type)
