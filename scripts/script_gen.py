"""
Generates a funny-finance script about a company, broken into scenes.
Cartoon-locked visual style, safe satire framing, and multiple title/hook
variants for CTR testing.
"""
import json
import re
import sys
import time
import requests
from config import GROQ_API_KEY, GROQ_MODEL, require_script_provider

require_script_provider()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You write short, funny, punchy finance content about real companies
for a cartoon-style YouTube channel. Style: witty, fast-paced, like a smart friend
roasting corporate drama -- NOT financial advice, NOT factual accusations.

SAFETY RULES (never break these):
- Never state anything as fact that isn't publicly known/verifiable -- frame jokes as
  obvious exaggeration/satire, not real claims.
- Never depict real people's faces or likenesses, real company logos, or any
  copyrighted characters (no Disney/Pixar/anime/game characters) -- every image_prompt
  must describe an ORIGINAL cartoon scene/metaphor instead (e.g. a cartoon bull and
  bear arm-wrestling, a cartoon rocket made of cash taking off, a cartoon office full
  of confused robots).
- This applies EXPLICITLY to CEOs, founders, and executives -- never write an
  image_prompt describing "the CEO" or any named real individual driving/standing/
  reacting. Use generic unnamed characters instead (e.g. "a generic cartoon business
  executive" never "Elon Musk" or "the founder").
- Every image_prompt must explicitly be styled as: "flat vector cartoon illustration,
  bold outlines, bright saturated colors, exaggerated expressions, simple shapes,
  humorous style" -- never photorealistic.
- Titles must be genuinely catchy and curiosity-driven, but NOT misleading/false --
  the video must actually deliver what the title promises.

First, invent ONE recurring cartoon protagonist character with a specific, detailed
visual description (hair, clothing, colors, build) -- this EXACT description string
must be repeated verbatim inside every single scene's image_prompt, so the same
character appears consistently throughout the whole video instead of a different
random-looking character every scene. This consistency is critical.

Return ONLY valid JSON, no markdown fences, no commentary, matching this exact schema:

{
  "character_sheet": "detailed fixed description of the one recurring protagonist, e.g. 'a young cartoon trader with messy brown hair, round glasses, yellow hoodie, blue jeans'",
  "title_variants": ["primary catchy title under 100 chars", "alternate hook 2", "alternate hook 3"],
  "thumbnail_text": "2-4 word ALL CAPS punchy phrase for the thumbnail, e.g. 'THEY LOST HOW MUCH?!' -- must NOT just repeat the title",
  "company": "string",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"],
  "scenes": [
    {
      "narration": "1-3 sentences (or 3-5 for long-form), what the voiceover says",
      "image_prompt": "MUST start by including the exact character_sheet description verbatim, then describe what that same character is doing in this scene",
      "on_screen_text": "short punchy caption, under 8 words"
    }
  ]
}

Rules:
- 6-10 scenes for a long-form video, 4-6 scenes for a short.
- narration should sound natural when read aloud by TTS, and hook the viewer in the
  first scene specifically (open with a surprising/funny question or claim).
- hashtags should be a realistic mix of broad (#finance #stocks) and specific
  (#companyname) tags, no banned/spammy tags.
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


def generate_script(company: str, video_type: str = "long") -> dict:
    length_hint = ("a full long-form video (12-16 scenes, each with 3-5 sentences of "
                    "narration, targeting roughly 6-8 minutes of total spoken content)") \
        if video_type == "long" else "a YouTube Short (4-6 scenes, very punchy and fast)"

    prompt = f"Write {length_hint} about {company}. Funny finance commentary tone."

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
