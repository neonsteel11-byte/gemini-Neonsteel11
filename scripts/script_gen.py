"""
Generates a funny-finance script about a company, broken into scenes.
Each scene = {narration, image_prompt, on_screen_text}.

Default provider: Groq (genuinely free tier, no card, no billing account --
sidesteps Google's ongoing AQ/AIza key rollout issues entirely).
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
for YouTube. Style: witty, fast-paced, like a smart friend roasting corporate drama,
NOT financial advice. Avoid defamation -- stick to publicly known facts, earnings,
stock moves, CEO antics, product flops/wins, and use humor/exaggeration clearly framed
as commentary, not factual accusation.

Return ONLY valid JSON, no markdown fences, no commentary, matching this exact schema:

{
  "title": "string, catchy, under 100 chars",
  "company": "string",
  "scenes": [
    {
      "narration": "1-3 sentences, what the voiceover says",
      "image_prompt": "detailed visual description for an AI image generator, no text/logos, safe-for-work, describes a scene/metaphor illustrating the narration",
      "on_screen_text": "short punchy caption, under 8 words"
    }
  ]
}

Rules:
- 6-10 scenes for a long-form video, 4-6 scenes for a short.
- image_prompt must NEVER ask for real company logos, real people's faces, or copyrighted
  characters -- describe generic/metaphorical business scenes instead.
- narration should sound natural when read aloud by TTS.
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
    required_top = {"title", "company", "scenes"}
    if not required_top.issubset(data.keys()):
        print(f"FATAL: script JSON missing required keys. Got: {list(data.keys())}",
              file=sys.stderr)
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
    length_hint = "a full long-form video (12-16 scenes, each with 3-5 sentences of narration, targeting roughly 6-8 minutes of total spoken content)" if video_type == "long" \
        else "a YouTube Short (4-6 scenes, very punchy and fast)"

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
