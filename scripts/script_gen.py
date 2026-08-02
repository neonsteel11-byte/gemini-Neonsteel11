"""
Generates a second-person POV, introspective financial-psychology narrative
script, matching the high-retention "animated documentary" style used by
successful faceless finance channels (moody, specific, emotionally grounded --
not comedic roast content).

DUAL API SUPPORT: Groq (primary, fast) → Gemini (backup, higher quality)
"""
import json
import re
import sys
import time
import requests
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, require_script_provider

require_script_provider()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

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

CLARITY CHECK: after writing each line, ask "would a 12-year-old understand this
instantly, out loud, on first listen?" If no, rewrite it simpler. This matters more
than sounding clever.

EXAMPLE JOKES (match this exact energy -- notice how SIMPLE and CLEAR these are):
- "You check your portfolio at 2am. Not because you need to. Because pain is a personality trait now."
- "Your friend says 'diamond hands.' Your hands are shaking so hard they're basically maracas."
- "The stock is down 12%. Your therapist is up 12%. Coincidence? Absolutely not."
- "You bought the dip. Then it dipped again. You have discovered a new geological formation: the trench."
Study the rhythm above -- specific, self-deprecating, an unexpected comparison as the
punchline. Every joke in the script must hit at this level or better.
- SIMPLE, CLEAR LANGUAGE ONLY -- write like you are explaining it to a smart 12-year-old.
  Short sentences. Common everyday words. If you use ANY financial term (stock, dip,
  shares, market cap, etc.), immediately explain what it means in plain words in the
  SAME sentence. Never assume the viewer already knows finance vocabulary.
  Use ONE clear, easy-to-picture specific detail per scene, not a pile of jargon-heavy
  details. A simple real number people can quickly picture ("$50") beats a complex
  one ("$2,143,000") if it makes the joke land faster.
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
  "description": "4-6 sentence genuinely well-written, specific, SEO-rich description covering what actually happens in the video, using natural keyword phrases people would search (not generic filler), written like a real professional creator wrote it personally -- specific, not templated",
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


def _call_groq(prompt: str, max_retries: int = 3):
    """Call Groq API with retry logic."""
    if not GROQ_API_KEY:
        return None
    
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

    print(f"  Groq unavailable after {max_retries} retries: {last_error}", file=sys.stderr)
    return None


def _call_gemini(prompt: str):
    """Call Gemini API as backup."""
    if not GEMINI_API_KEY:
        return None
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # Gemini uses a different format
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{SYSTEM_PROMPT}\n\nUser request: {prompt}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.9,
            "responseMimeType": "application/json",
        }
    }
    
    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"  Gemini error: HTTP {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Gemini exception: {e}", file=sys.stderr)
        return None


def _call_with_retry(prompt: str):
    """Try Groq first, then fall back to Gemini."""
    print("  Attempting script generation via Groq (primary)...")
    result = _call_groq(prompt)
    
    if result:
        print("  ✓ Groq script generation successful")
        return result
    
    print("   Groq failed, falling back to Gemini (backup)...")
    result = _call_gemini(prompt)
    
    if result:
        print("  ✓ Gemini script generation successful")
        return result
    
    print("FATAL: Both Groq and Gemini failed for script generation.", file=sys.stderr)
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
        print(f"FATAL: script JSON missing required keys. Got: {list(data.keys())}", file=sys.stderr)
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

    # Try Groq first
    raw_text = _call_groq(prompt)
    
    # Fall back to Gemini
    if not raw_text:
        raw_text = _call_gemini(prompt)
    
    if not raw_text:
        print(f"FATAL: Both APIs failed generating comparison script", file=sys.stderr)
        sys.exit(1)

    data = _extract_json(raw_text)
    return _validate_script(data)


INVENTION_SYSTEM_PROMPT = """You write short, fascinating "surprising true story"
scripts that are BOTH genuinely funny AND educational -- entertainment first, facts
woven in naturally, never a dry documentary lecture. Tone: like your funniest friend
telling you a wild true story, not a museum narrator.

EVERY SCENE NEEDS AN ACTUAL JOKE, not just an interesting fact. Structure: state the
real fact, then add a punchline -- an unexpected comparison, a modern reference, or
a blunt honest reaction. Examples of the right energy (write NEW jokes in this style,
never copy these):
- "He didn't wash his lab dishes for two weeks. Two weeks. And that's how we got
   penicillin. Never underestimate a man who just doesn't feel like doing chores."
- "The recipe got the temperature wrong by accident. Nobody fixed it. It's now a
   billion-dollar snack. Sometimes failure just tastes better."
Study the rhythm: real fact, then a sharp, funny turn. Every single scene must hit
this bar, not just the opening.

CRITICAL -- REAL DATA SHOWS VIEWERS LEAVE WITHIN THE FIRST 3 SECONDS if the opening is
slow. The VERY FIRST WORDS of scene 1 must be the single most shocking/surprising fact
or question from the whole story -- no setup, no "let me tell you about", no scene-
setting. Start mid-shock. Example: NOT "This is a story about a man who..." but instead
"A man had a metal rod go straight through his skull. He lived. And got smarter."

RULES:
- Use ONLY the real facts provided -- never invent facts.
- Scene 1 = the shock hook, zero preamble, zero pleasantries, active voice, first word
  must grab attention immediately.
- image_prompt for each scene should show ACTION or a big REACTION (surprised face,
  dramatic gesture, something happening) -- avoid static posed portraits, they read
  as boring/textbook. Entertainment first.
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

    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


def generate_money_story_script(topic: str, topic_facts: str, video_type: str = "short") -> dict:
    length_hint = "4-6 scenes, punchy" if video_type == "short" else "8-10 scenes"
    prompt = (
        f"Write a {length_hint} funny, surprising documentary-style story about "
        f"the real financial/money history event: {topic}.\n\n"
        f"Real facts:\n{topic_facts}"
    )

    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


LISTICLE_SYSTEM_PROMPT = """You write high-retention numbered-list videos about money
habits and financial psychology (e.g. "7 things smart people stop buying"). These are
general observations/opinions for entertainment and reflection -- NEVER present as
professional financial advice.

RULES:
- Structure as a numbered countdown, one item per scene.
- Each item: a short punchy statement, then ONE sentence of relatable explanation.
- Simple, clear language -- a smart 12-year-old must understand it instantly.
- Open with a strong hook stating the full list topic and a number (e.g. "5 things
  smart people quietly stop buying -- number 3 will surprise you").
- Tone: relatable, a little blunt, like honest advice from a friend, not preachy.

Return ONLY valid JSON matching the same schema as before, with "character_sheet",
"title_variants", "thumbnail_text", "company" (the list topic), "hashtags", and
"scenes" (one scene per list item plus an opening hook scene).
"""


WHITEBOARD_STYLE = (
    ", whiteboard animation style, hand-drawn marker illustration on a cream white "
    "background, simple bold black outline sketches, minimal color accents in "
    "amber/gold and navy blue marker colors, clean simple doodle-style icons, "
    "looks hand-drawn but neat and legible, no photorealism, no gritty texture"
)


def generate_listicle_script(topic: str, video_type: str = "short") -> dict:
    count = "5" if video_type == "short" else "10"
    prompt = f"Write a numbered list video: '{count} {topic}'. Every image_prompt " \
             f"must end with this exact style tag: {WHITEBOARD_STYLE}"

    raw_text = _call_with_retry(prompt)
    data = _extract_json(raw_text)
    return _validate_script(data)


if __name__ == "__main__":
    company_arg = sys.argv[1] if len(sys.argv) > 1 else "Tesla"
    result = generate_script(company_arg, "short")
    print(json.dumps(result, indent=2))
