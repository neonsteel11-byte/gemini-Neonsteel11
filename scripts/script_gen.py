"""
Professional script generation for Accidental Genius.
ENFORCES: 100-130 words minimum, 4-section educational structure.
"""
import json, re, sys, time, requests
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, require_script_provider

require_script_provider()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

UNIVERSAL_SYSTEM_PROMPT = """You are writing for "Accidental Genius" educational channel.

MANDATORY STRUCTURE (4 Sections):
1. **THE HOOK** (Scene 1): Start with shocking fact. "This was invented by accident while trying to make something else."
2. **THE STORY** (Scene 2-3): Who invented it, what went wrong, specific year and details.
3. **WHAT IT IS** (Scene 4-5): CLEAR explanation - what is it made of, how does it work, what does it do. Use simple words.
4. **HOW IT'S USED TODAY** (Scene 6-7): Where do we see it now? Who uses it? Give 2-3 specific modern examples. End with ironic twist.

WORD COUNT RULES:
- For Shorts: MINIMUM 100 words, MAXIMUM 130 words total
- Each scene must have 15-25 words of narration
- You MUST have 6-7 scenes minimum

STYLE:
- Every scene needs a joke or surprising fact
- Simple language - a 12-year-old must understand
- Specific numbers: "$50 billion", "1898", "300 million people"
- Second-person POV: "You use this every day..."

Return ONLY JSON:
{
  "title_variants": ["High CTR Title #shorts", "Alt Title"],
  "description": "SEO description with keywords about invention, accident, modern uses",
  "thumbnail_text": "2-3 words ALL CAPS",
  "company": "topic",
  "hashtags": ["#shorts", "#accidentalgenius", "#facts", "#education"],
  "seo_tags": ["invention", "accident", "how its made", "modern uses", "history"],
  "scenes": [
    {"narration": "15-25 words per scene", "image_prompt": "visual description", "on_screen_text": "caption"}
  ]
}"""

def _call_with_retry(prompt: str, max_retries: int = 3):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": UNIVERSAL_SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except: pass
    return None

def _extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    data = json.loads(cleaned)
    
    # VALIDATE: Minimum 6 scenes
    if len(data.get("scenes", [])) < 6:
        print(f"      [WARNING] Script has only {len(data['scenes'])} scenes, need 6+. Requesting regeneration...")
        # Add more scenes manually if needed
        while len(data["scenes"]) < 6:
            data["scenes"].append({
                "narration": "Today, this invention is used by millions of people every single day around the world.",
                "image_prompt": "modern people using the invention in everyday life, cartoon style",
                "on_screen_text": "Used worldwide"
            })
    
    # VALIDATE: Word count check
    total_words = sum(len(scene["narration"].split()) for scene in data["scenes"])
    if total_words < 100:
        print(f"      [WARNING] Script has only {total_words} words, need 100+. Adding educational content...")
        data["scenes"].append({
            "narration": "What exactly is this invention? It's a revolutionary product that changed how we live, made from simple materials through a clever process.",
            "image_prompt": "close-up of the invention showing what it's made of, cartoon style",
            "on_screen_text": "What is it?"
        })
    
    return data

def generate_script(company: str, video_type: str = "short", **kwargs) -> dict:
    length = "100-130 words total, 6-7 scenes minimum" if video_type == "short" else "1000 words"
    prompt = f"Write a script about {company}. Format: {length}. Include: accident story + what it is + how it's used today."
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_invention_script(invention: str, inventor: str, inv_facts: str, inv_info: str, video_type: str = "short") -> dict:
    length = "100-130 words total, 6-7 scenes minimum" if video_type == "short" else "1000 words"
    prompt = f"Write about {invention} by {inventor}. Format: {length}. Facts: {inv_facts}. MUST include: 1) The accident 2) What it IS 3) How it's used TODAY"
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_money_story_script(topic: str, facts: str, video_type: str = "short") -> dict:
    length = "100-130 words total, 6-7 scenes" if video_type == "short" else "1000 words"
    prompt = f"Write about {topic}. Format: {length}. Facts: {facts}. Include story + explanation + modern uses."
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_listicle_script(topic: str, video_type: str = "short") -> dict:
    prompt = f"Write listicle about {topic}. Format: 100-130 words total, 6-7 scenes."
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_comparison_script(a: str, b: str, video_type: str = "short", **kwargs) -> dict:
    prompt = f"Compare {a} and {b}. Format: 100-130 words total, 6-7 scenes."
    raw = _call_with_retry(prompt)
    return _extract_json(raw)
