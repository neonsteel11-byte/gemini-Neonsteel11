"""
Professional script generation for Accidental Genius channel.
Covers: Accidental inventions, bizarre original purposes, and hidden history.
Always includes: The shock hook, the story, WHAT it is, and HOW it's used today.
"""
import json
import re
import sys
import time
import requests
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, require_script_provider

require_script_provider()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

UNIVERSAL_SYSTEM_PROMPT = """You are a master YouTube scriptwriter for "Accidental Genius", 
an educational channel about the hidden, weird, and accidental history of everyday things.

YOUR SCRIPTS MUST INCLUDE THESE 4 SECTIONS:

**SECTION 1: THE SHOCK HOOK (Scene 1)**
- Start with the MOST shocking/contradictory fact in the first 3 seconds.
- Example: "This was originally invented as a torture device. Now you use it at the gym."
- NO setup, NO "let me tell you about" - start MID-SHOCK.

**SECTION 2: THE WEIRD ORIGIN STORY (Scenes 2-4)**
- What was it originally created for? (The bizarre/accidental truth)
- Who created it and what went wrong (or right)?
- Use specific details: dates, locations, exact moments.

**SECTION 3: WHAT IT ACTUALLY IS (Scenes 5-6)**
- Clearly explain: What exactly IS this thing?
- Simple, clear language -- a smart 12-year-old must understand instantly.
- Describe what it's made of or how it basically works.

**SECTION 4: HOW IT'S USED TODAY & MODERN IMPACT (Scenes 7-10)**
- WHERE is it used today? (homes, hospitals, space, everyday life)
- WHO uses it and HOW? (give 1-2 specific, relatable examples)
- How did it evolve from its weird original purpose to what it is now?
- End with a memorable, punchy fact or ironic twist about its legacy.

**STYLE RULES:**
- EVERY scene needs an actual joke, surprising fact, or "wait, what?" moment.
- Tone: Like your smartest, funniest friend telling you a wild true story.
- Use specific numbers: "$50 billion industry", "1857", "300 years ago".
- Simple language, short sentences, conversational rhythm.
- Second-person POV when possible: "You use this every day without thinking..."

**VISUAL RULES:**
- For historical figures: "USE_REAL_IMAGE: [person name] portrait"
- For objects/actions: describe the object/action clearly for cartoon illustration.
- For modern uses: show people USING the invention in relatable, everyday scenarios.
- NO text-bearing objects (signs, screens, newspapers with readable text).
- NO real logos or brand names.

Return ONLY valid JSON matching this schema:
{
  "character_sheet": "n/a",
  "title_variants": [
    "The [SHOCKING adjective] [accident/mistake/origin] That Gave Us [topic]",
    "How [topic] Was Originally Invented for [bizarre purpose]",
    "[Topic]: The [adjective] Truth You Were Never Taught"
  ],
  "description": "4-6 sentence SEO-rich description covering: the weird origin story + what it actually is + how it's used today + modern impact. Include keywords naturally.",
  "thumbnail_text": "2-4 word ALL CAPS punchy phrase (e.g., 'BY MISTAKE', 'DARK ORIGIN', 'NOT WHAT YOU THINK')",
  "company": "[topic name]",
  "hashtags": ["#AccidentalGenius", "#HiddenHistory", "#HowItsMade", "#ScienceFacts", "#Educational", "#DidYouKnow"],
  "seo_tags": ["[topic name]", "weird history of [topic]", "original purpose of [topic]", "how [topic] is used today", "accidental invention", "hidden facts", "educational documentary", "science history"],
  "scenes": [
    {
      "narration": "2-4 sentences mixing story + education + humor",
      "image_prompt": "USE_REAL_IMAGE: [person] portrait  OR  clear description of object/action/use case",
      "on_screen_text": "short caption under 8 words"
    }
  ]
}

SCENE COUNT:
- Shorts (60 sec): 6-8 scenes total
- Long-form (10-15 min): 12-15 scenes total

CRITICAL: Balance entertainment (60%) with practical education (40%). Viewers should laugh AND learn something they can share at a dinner party.
"""


def _call_with_retry(prompt: str, max_retries: int = 5):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": UNIVERSAL_SYSTEM_PROMPT},
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

    print(f"  Groq unavailable, trying Gemini fallback...", file=sys.stderr)
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(f"{UNIVERSAL_SYSTEM_PROMPT}\n\nUser: {prompt}")
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


def generate_script(company: str, video_type: str = "short", news_headlines: list = None, angle: str = None, avoid_titles: list = None) -> dict:
    length_hint = "6-8 scenes, 60 seconds total" if video_type == "short" else "12-15 scenes, 10-15 minutes"
    prompt = f"Write a {length_hint} script about the hidden history of **{company}**. {angle or ''}"
    if news_headlines:
        prompt += f"\nRecent context: {'; '.join(news_headlines[:3])}"
    
    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


def generate_invention_script(invention: str, inventor: str, inventor_facts: str, invention_facts: str, video_type: str = "short") -> dict:
    length_hint = "6-8 scenes" if video_type == "short" else "12-15 scenes"
    prompt = (
        f"Write a {length_hint} script about the accidental invention of **{invention}** by **{inventor}**.\n\n"
        f"Inventor facts: {inventor_facts}\nInvention facts: {invention_facts}\n\n"
        f"CRITICAL: Include sections on: 1. The shocking accident, 2. What it IS, 3. HOW it's used today, 4. Modern impact."
    )
    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


def generate_money_story_script(topic: str, topic_facts: str, video_type: str = "short") -> dict:
    length_hint = "6-8 scenes" if video_type == "short" else "12-15 scenes"
    prompt = f"Write a {length_hint} educational script about {topic}.\nFacts: {topic_facts}\nInclude: the story + what it is + how it's used + modern impact."
    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


def generate_listicle_script(topic: str, video_type: str = "short") -> dict:
    count = "5" if video_type == "short" else "10"
    prompt = f"Write a numbered list video: '{count} {topic}'. Include practical uses and weird origins for each item."
    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


def generate_comparison_script(company_a: str, company_b: str, video_type: str = "short", news_a: list = None, news_b: list = None) -> dict:
    length_hint = "6-8 scenes" if video_type == "short" else "12-15 scenes"
    prompt = f"Write a {length_hint} 'guess which one' comparison video between {company_a} and {company_b}. Include their weird origins and modern uses."
    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)
