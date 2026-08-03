"""
Professional script generation for Accidental Genius channel.
Includes: invention story + practical uses + modern applications + how-to-use.
Optimized for high CTR, retention, and educational value.
"""
import json
import re
import sys
import time
import requests
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, require_script_provider

require_script_provider()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

INVENTION_SYSTEM_PROMPT = """You are a professional YouTube scriptwriter for "Accidental Genius" - 
an educational channel about accidental inventions that changed the world.

YOUR SCRIPTS MUST INCLUDE THESE 5 SECTIONS:

**SECTION 1: THE SHOCK HOOK (Scene 1)**
- Start with the MOST shocking fact in the first 3 words
- Example: "A chef RUINED these potatoes on purpose. They became a billion-dollar snack."
- NO setup, NO "let me tell you about" - start MID-SHOCK

**SECTION 2: THE ACCIDENT STORY (Scenes 2-4)**
- What was the inventor TRYING to create?
- What went wrong? (the accident)
- Who was the inventor? (real person, real background)
- Use specific details: dates, locations, exact moments

**SECTION 3: WHAT IT IS (Scenes 5-6)**
- Clearly explain: What exactly IS this invention?
- Simple, clear language - a smart 12-year-old must understand
- Describe what it's made of, how it works (basically)
- Example: "Potato chips are thin slices of potato, fried until crispy, then salted."

**SECTION 4: HOW IT'S USED TODAY (Scenes 7-9)**
- WHERE is this invention used? (homes, hospitals, space, etc.)
- WHO uses it? (chefs, doctors, kids, engineers, etc.)
- HOW do people use it? (step-by-step simple explanation)
- Real-world applications: everyday life, industry, technology
- Modern innovations: how it evolved from the original

**SECTION 5: THE IMPACT (Final scenes)**
- How did this accident change the world?
- How much money does it make now? (specific numbers)
- Ironic twist: the inventor's reaction, what they originally wanted vs. what happened
- End with a memorable punchy fact

**STYLE RULES:**
- EVERY scene needs an actual joke or surprising fact
- Tone: like your smartest, funniest friend telling you a wild true story
- Use specific numbers: "$50 billion industry" not "very successful"
- Include real names, dates, places
- Simple language, short sentences, conversational
- Second-person POV when possible: "You use this every day..."

**VISUAL RULES:**
- For inventor portrait scenes: "USE_REAL_IMAGE: [inventor name] portrait"
- For invention scenes: describe the object/action clearly for cartoon illustration
- For modern uses: show people USING the invention in real scenarios
- NO text-bearing objects (signs, screens, newspapers with readable text)
- NO real logos or brand names

Return ONLY valid JSON matching this schema:
{
  "character_sheet": "n/a",
  "title_variants": [
    "The [SHOCKING adjective] [accident/mistake] That Gave Us [invention]",
    "How [inventor] ACCIDENTALLY [verb] [invention]",
    "[Invention]: The $[amount] [accident/mistake]"
  ],
  "description": "4-6 sentence SEO-rich description covering: the accident story + what it is + how it's used today + modern impact. Include keywords: [invention name], accidental invention, [inventor name], how it's used, modern applications",
  "thumbnail_text": "2-4 word ALL CAPS punchy phrase (e.g., 'ACCIDENT!', 'BY MISTAKE', '$1B ERROR')",
  "company": "[invention name]",
  "hashtags": ["#AccidentalGenius", "#InventionStory", "#[InventionName]", "#HowItsMade", "#ScienceHistory", "#Educational"],
  "seo_tags": ["[invention name]", "accidental invention", "[inventor name]", "how [invention] is made", "uses of [invention]", "modern applications", "invention history", "science documentary", "educational content", "how it works"],
  "scenes": [
    {
      "narration": "2-4 sentences mixing story + education + humor",
      "image_prompt": "USE_REAL_IMAGE: [inventor] portrait  OR  clear description of invention/action/use case",
      "on_screen_text": "short caption under 8 words"
    }
  ]
}

SCENE COUNT:
- Shorts (60 sec): 6-8 scenes total
- Long-form (10-15 min): 12-15 scenes total

CRITICAL: Balance entertainment (60%) with education (40%). Viewers should laugh AND learn something practical they can use in conversation.
"""


def _call_with_retry(prompt: str, max_retries: int = 5):
    """Try Groq first, fall back to Gemini."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": INVENTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }

    delay = 3
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            transient = resp.status_code in (429, 500, 502, 503)
            last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
            if not transient:
                print(f"  Groq non-transient error: {last_error}", file=sys.stderr)
                return None
        except Exception as e:
            last_error = str(e)

        print(f"  Groq rate-limited (attempt {attempt}/{max_retries}), retrying in {delay}s...", file=sys.stderr)
        time.sleep(delay)
        delay = min(delay * 2, 30)

    print(f"  Groq unavailable, trying Gemini...", file=sys.stderr)
    
    # Fallback to Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(f"{INVENTION_SYSTEM_PROMPT}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        print(f"FATAL: Both Groq and Gemini failed: {e}", file=sys.stderr)
        sys.exit(1)


def _extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"FATAL: Invalid JSON. Error: {e}", file=sys.stderr)
        sys.exit(1)


def _validate_script(data: dict) -> dict:
    required = {"character_sheet", "title_variants", "thumbnail_text", "company", "hashtags", "scenes"}
    if not required.issubset(data.keys()):
        print(f"FATAL: Missing keys: {required - set(data.keys())}", file=sys.stderr)
        sys.exit(1)
    if not data["scenes"]:
        print("FATAL: No scenes in script", file=sys.stderr)
        sys.exit(1)
    return data


def generate_invention_script(invention: str, inventor: str, inventor_facts: str,
                               invention_facts: str, video_type: str = "short") -> dict:
    """Generate professional invention script with story + uses + applications."""
    length_hint = "6-8 scenes, 60 seconds total" if video_type == "short" else "12-15 scenes, 10-15 minutes"
    
    prompt = (
        f"Write a {length_hint} script about the accidental invention of **{invention}** "
        f"by **{inventor}**.\n\n"
        f"Real facts about {inventor}: {inventor_facts}\n\n"
        f"Real facts about {invention}: {invention_facts}\n\n"
        f"CRITICAL: Include sections on:\n"
        f"1. The shocking accident story\n"
        f"2. What {invention} actually IS (clear explanation)\n"
        f"3. HOW people use {invention} today (practical applications)\n"
        f"4. WHERE it's used (homes, industry, technology, etc.)\n"
        f"5. Modern impact and ironic twist"
    )

    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


def generate_money_story_script(topic: str, topic_facts: str, video_type: str = "short") -> dict:
    length_hint = "6-8 scenes" if video_type == "short" else "12-15 scenes"
    prompt = (
        f"Write a {length_hint} educational script about {topic}.\n"
        f"Real facts: {topic_facts}\n"
        f"Include: the story + what it is + how it's used + modern impact"
    )
    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


def generate_listicle_script(topic: str, video_type: str = "short") -> dict:
    count = "5" if video_type == "short" else "10"
    prompt = f"Write a numbered list video: '{count} {topic}'. Include practical uses for each item."
    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


if __name__ == "__main__":
    # Test
    result = generate_invention_script(
        "Penicillin", "Alexander Fleming", 
        "Scottish biologist, 1928, forgot to wash dishes",
        "First antibiotic, killed bacteria, saved millions of lives",
        "short"
    )
    print(json.dumps(result, indent=2))
