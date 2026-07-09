"""
Generates a funny-finance script about a company, broken into scenes.
Cartoon-locked visual style, real-news-grounded content, actual joke
structure (not vague filler), and multiple title/hook variants for CTR.
"""
import json
import re
import sys
import time
import requests
from config import GROQ_API_KEY, GROQ_MODEL, require_script_provider

require_script_provider()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You write funny, SPECIFIC finance commentary about real companies
for a cartoon YouTube channel. This is NOT financial advice, and jokes must be framed
as obvious satire/exaggeration, not factual claims.

CRITICAL QUALITY RULES -- generic, vague content is a FAILURE:
- Every scene must reference a SPECIFIC real fact, number, event, or recent headline
  provided to you -- never write vague filler like "wild ride" or "big changes" with
  no substance. If no real news is provided, invent ONE specific plausible-sounding
  concrete detail (a number, a quote-style line, a specific event) rather than staying
  vague -- specificity is what makes it funny AND informative.
- Every joke needs an actual SETUP and PUNCHLINE structure -- state a fact, then twist
  it with an unexpected comparison, exaggeration, or reaction. Never just narrate facts
  flatly with no comedic turn.
- Open scene 1 with a genuinely surprising hook -- a real number, a shocking comparison,
  or a direct question that creates curiosity. Never open generically.
- The viewer should walk away knowing at least one real, specific thing about the
  company that they didn't know before, PLUS having laughed at least twice.

SAFETY RULES (never break these):
- Never state anything as fact that isn't grounded in the provided real news OR clearly
  framed as satire/exaggeration.
- Never depict real people's faces or likenesses, real company logos, or any
  copyrighted characters. This applies EXPLICITLY to CEOs/founders/executives -- use
  a generic unnamed cartoon character instead, never a named real individual.
- Every image_prompt must be styled as flat vector cartoon illustration, bold outlines,
  bright colors, no text/logos.
- NEVER describe a sign, banner, billboard, screen, phone display, newspaper, or any
  object that would contain readable text -- image models render these as garbled
  gibberish. Describe actions, expressions, and objects WITHOUT text instead (e.g.
  "a character staring at a glowing phone" NOT "a phone showing a stock chart with
  numbers"; "a worried character near a factory" NOT "a factory with a banner sign").

First, invent ONE recurring cartoon protagonist with a specific, detailed visual
description -- this EXACT description must be repeated verbatim inside every scene's
image_prompt, so the same character appears consistently throughout the video.

Return ONLY valid JSON, no markdown fences, no commentary, matching this exact schema:

{
  "character_sheet": "detailed fixed description of the one recurring protagonist",
  "title_variants": ["primary catchy SPECIFIC title under 100 chars referencing a real detail", "alternate hook 2", "alternate hook 3"],
  "thumbnail_text": "2-4 word ALL CAPS punchy phrase, specific not generic",
  "company": "string",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"],
  "scenes": [
    {
      "narration": "1-3 sentences (3-5 for long-form) with a real specific detail + a setup/punchline joke",
      "image_prompt": "starts with the exact character_sheet description, then what that character is doing in this specific scene",
      "on_screen_text": "short punchy caption, under 8 words"
    }
  ]
}

Rules:
- 6-10 scenes for a long-form video, 4-6 scenes for a short.
- narration should sound natural read aloud, fast-paced, punchy sentences.
"""


def _call_with_retry(prompt: str, max_retries: int = 5):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }

    delay = 5
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            transient = resp.status_code in (429, 500, 502, 503)
            last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
            if not transient:
                print(f"FATAL: non-transient Groq error: {last_error}", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            last_error = str(e)

        print(f"  Groq overloaded/rate-limited (attempt {attempt}/{max_retries}), "
              f"retrying in {delay}s...", file=sys.stderr)
        time.sleep(delay)
        delay = min(delay * 2, 60)

    print(f"FATAL: Groq still unavailable after {max_retries} retries: {last_error}",
          file=sys.stderr)
    sys.exit(1)


def _extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"FATAL: model did not return valid JSON. Raw output:\n{text}\n\nError: {e}",
              file=sys.stderr)
        sys.exit(1)


def _validate_script(data: dict) -> dict:
    required_top = {"character_sheet", "title_variants", "thumbnail_text", "company", "hashtags", "scenes"}
    if not required_top.issubset(data.keys()):
        print(f"FATAL: script JSON missing required keys. Got: {list(data.keys())}",
              file=sys.stderr)
        sys.exit(1)
    if not isinstance(data["title_variants"], list) or len(data["title_variants"]) < 2:
        print("FATAL: need at least 2 title_variants for CTR testing.", file=sys.stderr)
        sys.exit(1)
    if not data["scenes"] or not isinstance(data["scenes"], list):
        print("FATAL: script JSON has no scenes.", file=sys.stderr)
        sys.exit(1)
    for i, scene in enumerate(data["scenes"]):
        for key in ("narration", "image_prompt", "on_screen_text"):
            if not scene.get(key, "").strip():
                print(f"FATAL: scene {i} missing/empty '{key}'.", file=sys.stderr)
                sys.exit(1)
    return data


def generate_script(company: str, video_type: str = "long", news_headlines: list = None) -> dict:
    length_hint = ("a full long-form video (12-16 scenes, each with 3-5 sentences of "
                    "narration, targeting roughly 6-8 minutes of total spoken content)") \
        if video_type == "long" else "a YouTube Short (4-6 scenes, very punchy and fast)"

    news_block = ""
    if news_headlines:
        joined = "\n".join(f"- {h}" for h in news_headlines)
        news_block = (
            f"\n\nHere are REAL recent headlines about {company} -- base your specific "
            f"facts and jokes on these:\n{joined}\n"
        )
    else:
        news_block = (
            f"\n\nNo real news was available -- invent ONE specific plausible-sounding "
            f"concrete detail about {company} rather than staying vague.\n"
        )

    prompt = f"Write {length_hint} about {company}. Funny finance commentary tone.{news_block}"

    raw_text = _call_with_retry(prompt)

    if not raw_text or not raw_text.strip():
        print("FATAL: model returned an empty response for script generation.",
              file=sys.stderr)
        sys.exit(1)

    data = _extract_json(raw_text)
    return _validate_script(data)


if __name__ == "__main__":
    company_arg = sys.argv[1] if len(sys.argv) > 1 else "Tesla"
    result = generate_script(company_arg, "short")
    print(json.dumps(result, indent=2))
