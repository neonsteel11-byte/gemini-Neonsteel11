"""
Generates a second-person POV, introspective financial-psychology narrative
script, matching the high-retention "animated documentary" style used by
successful faceless finance channels (moody, specific, emotionally grounded --
not comedic roast content).
"""
import json
import re
import sys
import time
import requests
from config import GROQ_API_KEY, GROQ_MODEL, require_script_provider

require_script_provider()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a master YouTube scriptwriter specializing in high-retention,
FUNNY, second-person "POV" finance storytelling about big well-known companies. NOT
financial advice -- clearly satire/comedy, not factual claims.

NARRATIVE & STYLE RULES:
- Write exclusively in second-person ("You") / POV perspective. The viewer must feel
  like they are actively living the story -- e.g. "POV: you bought the dip" or
  "You just found out your company's stock did WHAT."
- Tone: genuinely FUNNY -- witty, self-aware, relatable financial-anxiety humor, like a
  smart friend narrating your own financial disaster back to you. Every scene needs an
  actual joke: a setup, then an unexpected twist/comparison/exaggeration as the
  punchline. Never flat narration with no comedic turn.

EXAMPLE JOKES (match this exact energy and structure, do not copy content):
- "You check your portfolio at 2am. Not because you need to. Because pain is a personality trait now."
- "Your friend says 'diamond hands.' Your hands are shaking so hard they're basically maracas."
- "The stock is down 12%. Your therapist is up 12%. Coincidence? Absolutely not."
- "You bought the dip. Then it dipped again. You have discovered a new geological formation: the trench."
Study the rhythm above -- specific, self-deprecating, an unexpected comparison as the
punchline. Every joke in the script must hit at this level or better.
- Hyper-specific realism: avoid vague phrases. Use exact, un-rounded numbers
  ("$2,143,000" not "two million dollars"), specific mundane details ("waking up at
  6:12 a.m. on a Tuesday", "a coffee stain on your shirt", "a spreadsheet named
  freedom_number_v14.xlsx"). Specificity is what makes it feel real and grip attention.
- Emotional core: go past the surface of money -- focus on identity loss, changing
  relationships with friends/family, scarcity anxiety, quiet moments of reflection.
- If real news/facts about the company are provided, weave in real specific figures
  from them (numbers, dates, events) to ground the story in reality.

VISUAL RULES (image prompts):
- CLEAN, BRIGHT, FLAT vector cartoon illustrations ONLY -- bold black outlines, simple
  shapes, saturated colors. NEVER painterly, photorealistic, gritty, heavily-shaded, or
  dark/noir-lit -- those render poorly and look messy at small sizes. Convey emotional
  weight through the character's POSE and EXPRESSION, not through dark lighting or
  detailed shading (e.g. "a simply-drawn cartoon character slumped at a bright desk,
  exaggerated worried expression" NOT "a man in shadow, moody cinematic lighting").
- NEVER describe real copyrighted logos, real people's faces/likenesses (including
  named CEOs/executives -- use a generic unnamed character), or any sign/banner/
  screen/newspaper with readable text -- image models render text as garbled
  gibberish, so describe the emotional/visual content WITHOUT text-bearing objects.

Invent ONE recurring visual protagonist (the "you" of the story) with a fixed detailed
description -- repeat it verbatim in every scene's image_prompt for visual consistency.

Return ONLY valid JSON, no markdown fences, no commentary, matching this exact schema:

{
  "character_sheet": "detailed fixed description of the recurring protagonist character",
  "title_variants": ["PROFESSIONAL two-part title in format '[Punchy Hook]: [Specific Descriptive Stakes Clause]' -- e.g. 'The $2 Billion Mistake: How One Ballpoint Pen Company Almost Went Bankrupt' or 'POV: You Owned Tesla During The Great Recall Event' -- NEVER a short generic 2-3 word title", "alternate professional title 2", "alternate professional title 3"],
  "description": "2-3 sentence polished, professional video description summarizing the real content -- written like a documentary channel description, not clickbait filler",
  "thumbnail_text": "2-4 word ALL CAPS punchy phrase",
  "company": "string",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"],
  "seo_tags": ["10-15 specific real search-relevant keyword phrases, e.g. company name, topic, related terms people actually search"],
  "scenes": [
    {
      "narration": "1-3 sentences (3-5 for long-form), natural spoken-delivery, short sentences, conversational rhythm, second-person POV, hyper-specific details",
      "image_prompt": "starts with the exact character_sheet description, then a moody visual metaphor for this scene's emotional beat, no text-bearing objects",
      "on_screen_text": "short punchy caption, under 8 words"
    }
  ]
}

Rules:
- 6-10 scenes for long-form, 4-6 for a Short.
- Open scene 1 with a strong "POV:" or "You just..." hook that creates immediate
  curiosity about a specific financial/life situation involving the company.
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


def generate_script(company: str, video_type: str = "long", news_headlines: list = None, angle: str = None, avoid_titles: list = None) -> dict:
    length_hint = ("a full long-form video (10-14 scenes, each with 3-5 sentences of "
                    "narration, targeting roughly 10-14 minutes of total spoken content, "
                    "documentary-style pacing)") \
        if video_type == "long" else "a YouTube Short (4-6 scenes, punchy, fast POV hook)"

    news_block = ""
    if news_headlines:
        joined = "\n".join(f"- {h}" for h in news_headlines)
        news_block = (
            f"\n\nHere are REAL recent headlines about {company} -- weave specific real "
            f"facts/numbers from these into the story:\n{joined}\n"
        )
    else:
        news_block = (
            f"\n\nNo real news was available -- invent ONE specific plausible-sounding "
            f"concrete financial detail about {company} rather than staying vague.\n"
        )

    angle_line = f"Specific angle to use: {angle}" if angle else \
        "Pick any second-person POV angle involving an employee, investor, or customer."
    avoid_block = ""
    if avoid_titles:
        joined = "\n".join(f"- {t}" for t in avoid_titles[-15:])
        avoid_block = f"\n\nNEVER reuse or closely resemble any of these already-used titles:\n{joined}\n"

    prompt = (
        f"Write {length_hint}. {angle_line} The story involves {company}. "
        f"Introspective, psychological, hyper-specific tone.{news_block}{avoid_block}"
    )

    raw_text = _call_with_retry(prompt)

    if not raw_text or not raw_text.strip():
        print("FATAL: model returned an empty response for script generation.",
              file=sys.stderr)
        sys.exit(1)

    data = _extract_json(raw_text)
    return _validate_script(data)


COMPARISON_SYSTEM_PROMPT = """You write "GUESS WHICH ONE" comparison finance content --
a proven high-engagement format built around curiosity and audience guessing.

FORMAT RULES:
- Present two companies side by side without revealing the answer immediately.
- Scene 1-2: set up a specific, concrete comparison (e.g. "$1,000 invested in each of
  these two companies in 2020 -- one of them is worth way more today. Which one?").
  Use REAL numbers if news/facts are provided.
- Middle scenes: give 2-3 real, specific, teasing clues about each company (facts,
  recent news, without naming which is which yet) to keep viewers guessing.
- Final scene: dramatic reveal with the real answer and real numbers, plus a punchy
  reaction/joke.
- Explicitly prompt viewers to comment their guess before the reveal (e.g. "Comment
  which one you think it is before scene 4").
- Tone: FUNNY, second-person energy, genuine curiosity-driving suspense.

VISUAL RULES: same as standard -- clean flat vector cartoon, bold outlines, bright
colors, no text-bearing objects (no signs/screens/banners), no real people's faces,
no real logos. Invent one consistent visual style, reused character descriptions
across scenes.

Return ONLY valid JSON, same schema as before:
{
  "character_sheet": "...",
  "title_variants": ["GUESS WHICH ONE style title", "alt 2", "alt 3"],
  "thumbnail_text": "2-4 words, e.g. 'GUESS WHICH ONE'",
  "company": "CompanyA vs CompanyB",
  "hashtags": [...],
  "seo_tags": ["10-15 specific real search-relevant keyword phrases, e.g. company name, topic, related terms people actually search"],
  "scenes": [{"narration": "...", "image_prompt": "...", "on_screen_text": "..."}]
}
"""


def generate_comparison_script(company_a: str, company_b: str, video_type: str = "short",
                                 news_a: list = None, news_b: list = None) -> dict:
    length_hint = "4-6 scenes, punchy" if video_type == "short" else "8-12 scenes"
    news_block = ""
    if news_a:
        news_block += f"\n\nReal recent news about {company_a}:\n" + "\n".join(f"- {h}" for h in news_a)
    if news_b:
        news_block += f"\n\nReal recent news about {company_b}:\n" + "\n".join(f"- {h}" for h in news_b)

    prompt = (
        f"Write a {length_hint} 'guess which one' comparison video between "
        f"{company_a} and {company_b}.{news_block}"
    )

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": COMPARISON_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        print(f"FATAL: Groq error generating comparison script: {resp.status_code} {resp.text[:300]}",
              file=sys.stderr)
        sys.exit(1)

    raw_text = resp.json()["choices"][0]["message"]["content"]
    data = _extract_json(raw_text)
    return _validate_script(data)


INVENTION_SYSTEM_PROMPT = """You write short, fascinating "who actually invented this"
documentary-style scripts about everyday objects and their real inventors. Tone: genuinely
surprising, engaging, fact-driven -- like a great trivia friend, not dry or academic.

RULES:
- Use ONLY the real facts provided about the inventor and invention -- never invent facts.
- Open with a surprising hook (e.g. "The raincoat wasn't invented by a fashion designer --
  it was a chemist who accidentally ruined his coat.")
- Include real specific details: years, names, surprising twists in the story.
- 2-3 scenes should describe the REAL inventor (their portrait will be used as the image --
  so image_prompt for those scenes should just say "USE_REAL_IMAGE: inventor portrait").
- 1-2 scenes should describe the invention/object itself in use -- these can be clean flat
  cartoon illustrations (no text-bearing objects, no logos).
- End with a punchy surprising fact or ironic twist about the invention's legacy.

Return ONLY valid JSON matching this schema:
{
  "character_sheet": "not used for this format, put 'n/a'",
  "title_variants": ["surprising fact-style title", "alt 2", "alt 3"],
  "thumbnail_text": "2-4 words",
  "company": "the invention name",
  "hashtags": [...],
  "seo_tags": ["10-15 specific real search-relevant keyword phrases, e.g. company name, topic, related terms people actually search"],
  "scenes": [
    {"narration": "...", "image_prompt": "USE_REAL_IMAGE: inventor portrait  OR  a clean cartoon description", "on_screen_text": "..."}
  ]
}
"""


def generate_invention_script(invention: str, inventor: str, inventor_facts: str,
                               invention_facts: str, video_type: str = "short") -> dict:
    length_hint = "4-6 scenes, punchy" if video_type == "short" else "8-10 scenes"
    prompt = (
        f"Write a {length_hint} script about the real invention of the {invention}, "
        f"credited to {inventor}.\n\nReal facts about {inventor}:\n{inventor_facts}\n\n"
        f"Real facts about the {invention}:\n{invention_facts}"
    )

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": INVENTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        print(f"FATAL: Groq error generating invention script: {resp.status_code} {resp.text[:300]}",
              file=sys.stderr)
        sys.exit(1)

    raw_text = resp.json()["choices"][0]["message"]["content"]
    data = _extract_json(raw_text)
    return _validate_script(data)


if __name__ == "__main__":
    company_arg = sys.argv[1] if len(sys.argv) > 1 else "Tesla"
    result = generate_script(company_arg, "short")
    print(json.dumps(result, indent=2))
