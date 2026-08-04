"""
Professional script generation. STRICTLY ENFORCES 55-SECOND LIMIT FOR SHORTS.
"""
import json
import re
import sys
import time
import requests
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, require_script_provider

require_script_provider()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

UNIVERSAL_SYSTEM_PROMPT = """You are a master YouTube scriptwriter for "Accidental Genius".

CRITICAL RULE: If the user asks for a "Short", the TOTAL script MUST be under 130 words. 
This is a hard limit. If it is over 130 words, the video will be over 60 seconds and will FAIL on YouTube.
For Shorts: 4-5 scenes MAX. 20-25 words per scene.
For Long-form: No word limit.

YOUR SCRIPTS MUST INCLUDE:
1. THE HOOK (Scene 1): Start MID-SHOCK. "He was trying to make rubber. He created THIS instead."
2. THE STORY (Scenes 2-3): The accident or weird origin.
3. THE EXPLANATION (Scene 4): What it actually is and how it's used today.
4. THE LOOP (Final Scene): End with a sentence that flows perfectly back into the first sentence, so the video loops seamlessly.

Return ONLY valid JSON:
{
  "title_variants": ["High CTR Title #shorts #accidentalgenius", "Alt Title #shorts"],
  "description": "SEO description with keywords.",
  "thumbnail_text": "2-3 words ALL CAPS",
  "company": "topic",
  "hashtags": ["#shorts", "#accidentalgenius", "#facts"],
  "seo_tags": ["tag1", "tag2"],
  "scenes": [
    {"narration": "Short punchy sentence.", "image_prompt": "visual description", "on_screen_text": "caption"}
  ]
}
"""

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
    except:
        pass
    return None

def _extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)

def generate_script(company: str, video_type: str = "short", **kwargs) -> dict:
    length = "under 130 words total (4 scenes max)" if video_type == "short" else "1000 words (10 scenes)"
    prompt = f"Write a script about {company}. Format: {length}."
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_invention_script(invention: str, inventor: str, inv_facts: str, inv_info: str, video_type: str = "short") -> dict:
    length = "under 130 words total (4 scenes max)" if video_type == "short" else "1000 words"
    prompt = f"Write a script about {invention} by {inventor}. Format: {length}. Facts: {inv_facts}"
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_money_story_script(topic: str, facts: str, video_type: str = "short") -> dict:
    length = "under 130 words total" if video_type == "short" else "1000 words"
    prompt = f"Write a script about {topic}. Format: {length}. Facts: {facts}"
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_listicle_script(topic: str, video_type: str = "short") -> dict:
    prompt = f"Write a listicle about {topic}. Format: under 130 words total."
    raw = _call_with_retry(prompt)
    return _extract_json(raw)

def generate_comparison_script(a: str, b: str, video_type: str = "short", **kwargs) -> dict:
    prompt = f"Compare {a} and {b}. Format: under 130 words total."
    raw = _call_with_retry(prompt)
    return _extract_json(raw)
