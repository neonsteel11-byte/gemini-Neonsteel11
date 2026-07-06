"""
Generates a funny-finance script about a company, broken into scenes.
Each scene = {narration, image_prompt, on_screen_text}.

Fails loudly if Gemini returns anything that isn't valid, well-formed
scene data -- this is the #1 place silent failures start.
"""
import json
import re
import sys
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, require_gemini_key

require_gemini_key()
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

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
  characters -- describe generic/metaphorical business scenes instead (e.g. "a cartoon bull
  and bear arm wrestling on a trading floor" not "the Coinbase logo").
- narration should sound natural when read aloud by TTS.
"""


def _call_with_retry(prompt: str, max_retries: int = 5):
    """
    Retries on transient server errors (503 overloaded, 429 rate limit) with
    exponential backoff. This is the correct fix for the '503 UNAVAILABLE /
    high demand' error -- it's Google's servers being temporarily busy, not
    a bug in the request. Fails loudly only after genuinely exhausting retries.
    """
    delay = 5
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
        except Exception as e:
            msg = str(e)
            transient = any(code in msg for code in
                             ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "high demand"])
            last_error = e
            if not transient:
                print(f"FATAL: non-transient Gemini error: {msg}", file=sys.stderr)
                sys.exit(1)
            print(f"  Gemini overloaded/rate-limited (attempt {attempt}/{max_retries}), "
                  f"retrying in {delay}s...", file=sys.stderr)
            time.sleep(delay)
            delay = min(delay * 2, 60)

    print(f"FATAL: Gemini still unavailable after {max_retries} retries: {last_error}",
          file=sys.stderr)
    sys.exit(1)


def _extract_json(text: str) -> dict:
    """Strip markdown fences if Gemini adds them despite instructions."""
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"FATAL: Gemini did not return valid JSON. Raw output:\n{text}\n\nError: {e}",
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
    """
    video_type: "long" or "short"
    Returns validated dict: {title, company, scenes: [...]}
    """
    length_hint = "a full long-form video (6-10 scenes)" if video_type == "long" \
        else "a YouTube Short (4-6 scenes, very punchy and fast)"

    prompt = f"Write {length_hint} about {company}. Funny finance commentary tone."

    response = _call_with_retry(prompt)

    if not response.text or not response.text.strip():
        print("FATAL: Gemini returned an empty response for script generation.",
              file=sys.stderr)
        sys.exit(1)

    data = _extract_json(response.text)
    return _validate_script(data)


if __name__ == "__main__":
    # Quick manual test: python3 scripts/script_gen.py "Tesla"
    company_arg = sys.argv[1] if len(sys.argv) > 1 else "Tesla"
    result = generate_script(company_arg, "short")
    print(json.dumps(result, indent=2))
