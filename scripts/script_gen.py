import json, sys, time, requests
from config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def generate_invention_script(invention, inventor, facts, info, video_type="short"):
    if video_type == "long":
        length = "15-18 scenes, EACH scene must have 80-110 words of narration (this is a strict per-scene minimum, not a total to divide up)"
        min_scenes = 15
    else:
        length = "220-260 words, 9 scenes"
        min_scenes = 9

    prompt = f"""Write an educational short-video script about {invention}, invented by {inventor}.
Length: {length}.
Structure: 1) Shock hook 2) Weird origin story 3) What it actually is 4) How it is used today.
Facts to include: {facts}

Return ONLY valid JSON in EXACTLY this structure, with no missing fields:
{{
  "title_variants": ["title using a specific number or dollar amount", "title using a curiosity gap (e.g. Why {invention} Almost Failed)", "title using direct contradiction/surprise (e.g. He Was Trying to X, He Invented Y Instead)"],
  "description": "short video description",
  "thumbnail_text": "short punchy thumbnail text",
  "hashtags": ["#shorts", "#facts"],
  "seo_tags": ["tag1", "tag2"],
  "scenes": [
    {{"narration": "one or two sentences of spoken narration for this scene, no scene numbers or labels", "image_prompt": "specific visual description for this scene, cartoon style", "on_screen_text": "short on-screen caption, 2-5 words"}}
  ]
}}

Every scene MUST include narration, image_prompt, and on_screen_text. Do not skip any field. Do not include the words "scene 1" or scene numbers anywhere in narration text."""

    try:
        print(f"      Calling Groq API...")
        resp = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.9, "response_format": {"type": "json_object"}},
            timeout=90)

        resp_data = resp.json()
        if "choices" in resp_data and len(resp_data["choices"]) > 0:
            data = json.loads(resp_data["choices"][0]["message"]["content"])
            data.setdefault("scenes", [])

            for idx, scene in enumerate(data["scenes"]):
                scene.setdefault("narration", f"Here is another important fact about {invention}.")
                scene.setdefault("image_prompt", f"cartoon illustration of {invention}, bright colors")
                scene.setdefault("on_screen_text", "")

            while len(data["scenes"]) < min_scenes:
                data["scenes"].append({
                    "narration": f"The impact of {invention} on modern life is undeniable and massive.",
                    "image_prompt": f"cartoon showing {invention} being used worldwide",
                    "on_screen_text": "Global Impact"
                })

            data.setdefault("title_variants", [
                f"The ${invention} Mistake That Changed Everything",
                f"Why {invention} Almost Never Existed",
                f"{inventor} Was Trying to Fix Something Else"
            ])
            data.setdefault("description", f"Discover the hidden history of {invention}.")
            data.setdefault("thumbnail_text", "DID YOU KNOW?")
            data.setdefault("company", invention)
            data.setdefault("hashtags", ["#shorts", "#facts"])
            data.setdefault("seo_tags", [invention, "history"])

            print(f"      [OK] Script generated: {len(data['scenes'])} scenes")
            return data
    except Exception as e:
        print(f"      [!] API Error: {e}")

    print("      [!] Using dynamic fallback...")

    fallback_scenes = [
        {"narration": f"Did you know {invention} was created completely by accident?", "image_prompt": f"cartoon of {invention} with explosion effect", "on_screen_text": "By Accident!"},
        {"narration": f"{inventor} never intended to create {invention} - it was a total mistake.", "image_prompt": f"cartoon of {inventor} looking shocked", "on_screen_text": "Total Mistake"},
        {"narration": f"While trying to solve a different problem, {inventor} stumbled upon {invention}.", "image_prompt": f"cartoon laboratory accident creating {invention}", "on_screen_text": "Happy Accident"},
        {"narration": f"What exactly is {invention}? It's a revolutionary product that changed everything.", "image_prompt": f"close-up cartoon diagram of {invention}", "on_screen_text": "What Is It?"},
        {"narration": f"Before {invention}, people had to use much more difficult methods.", "image_prompt": f"cartoon showing life before {invention}", "on_screen_text": "Life Before"},
        {"narration": f"Today {invention} is used by billions of people every single day.", "image_prompt": f"cartoon showing {invention} used worldwide", "on_screen_text": "Used Worldwide"},
        {"narration": f"The {invention} industry is now worth billions of dollars globally.", "image_prompt": f"cartoon showing money and {invention}", "on_screen_text": "Billion Dollar Industry"},
    ]

    if video_type == "long":
        long_scenes = [
            {"narration": f"The original version of {invention} looked very different from today.", "image_prompt": f"cartoon showing old version of {invention}", "on_screen_text": "Original Design"},
            {"narration": f"It took years for {inventor} to perfect {invention}.", "image_prompt": f"cartoon timeline of {invention} development", "on_screen_text": "Years of Work"},
            {"narration": f"Early critics said {invention} would never catch on - they were wrong.", "image_prompt": f"cartoon of critics dismissing {invention}", "on_screen_text": "They Were Wrong"},
            {"narration": f"The manufacturing process for {invention} involves complex chemistry.", "image_prompt": f"cartoon factory making {invention}", "on_screen_text": "How It's Made"},
            {"narration": f"{invention} has evolved dramatically since {inventor} first created it.", "image_prompt": f"cartoon evolution of {invention}", "on_screen_text": "Evolution"},
            {"narration": f"Modern versions of {invention} are more advanced than ever before.", "image_prompt": f"cartoon showing modern high-tech {invention}", "on_screen_text": "Modern Version"},
            {"narration": f"Scientists are still finding new uses for {invention} today.", "image_prompt": f"cartoon scientists researching {invention}", "on_screen_text": "New Uses"},
            {"narration": f"The environmental impact of {invention} is now being studied carefully.", "image_prompt": f"cartoon showing eco-friendly {invention}", "on_screen_text": "Environmental Impact"},
        ]
        fallback_scenes.extend(long_scenes)

    return {
        "title_variants": [f"The Accident That Created {invention}", f"Why {inventor} Almost Gave Up on {invention}", f"{invention}: The Billion-Dollar Mistake"],
        "description": f"Discover the hidden history of {invention} and how {inventor} created it by accident.",
        "thumbnail_text": "BY MISTAKE!",
        "company": invention,
        "hashtags": ["#shorts", "#accidentalgenius", f"#{invention.replace(' ','').lower()}"],
        "seo_tags": [invention, inventor, "accidental invention", "history facts", "how its made"],
        "scenes": fallback_scenes[:min_scenes]
    }


def generate_script(company, video_type="short", **kwargs):
    return generate_invention_script(company, "Unknown", "", "", video_type)


def generate_money_story_script(topic, facts, video_type="short"):
    """Generates a script for a wild historical/financial STORY (not an invention).
    Uses its own prompt and fallback, since 'invented by X' framing doesn't fit
    story titles like 'How Ancient Spice Routes Accidentally Created Modern Banking'."""
    if video_type == "long":
        length = "15-18 scenes, EACH scene must have 80-110 words of narration (strict per-scene minimum)"
        min_scenes = 15
    else:
        length = "140-170 words, 7 scenes"
        min_scenes = 7

    prompt = f"""Write an educational short-video script telling the true story of: {topic}.
Length: {length}.
Structure: 1) Shock hook 2) How the events unfolded 3) The surprising twist or consequence 4) Why it still matters today.
Facts to include: {facts}

Return ONLY valid JSON in EXACTLY this structure, with no missing fields:
{{
  "title_variants": ["title using a number or striking detail", "title using a curiosity gap", "title using direct contradiction/surprise"],
  "description": "short video description",
  "thumbnail_text": "short punchy thumbnail text",
  "hashtags": ["#shorts", "#facts"],
  "seo_tags": ["tag1", "tag2"],
  "scenes": [
    {{"narration": "one or two sentences of spoken narration for this scene, no scene numbers or labels", "image_prompt": "specific visual description for this scene, realistic detailed illustration", "on_screen_text": "short on-screen caption, 2-5 words"}}
  ]
}}

Every scene MUST include narration, image_prompt, and on_screen_text. Do not skip any field. Do not include the words "scene 1" or scene numbers anywhere in narration text."""

    try:
        print("      Calling Groq API for story...")
        resp = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.9, "response_format": {"type": "json_object"}},
            timeout=90)
        resp_data = resp.json()
        if "choices" in resp_data and len(resp_data["choices"]) > 0:
            data = json.loads(resp_data["choices"][0]["message"]["content"])
            data.setdefault("scenes", [])
            for idx, scene in enumerate(data["scenes"]):
                scene.setdefault("narration", f"Here is another key detail about this story.")
                scene.setdefault("image_prompt", f"realistic detailed illustration related to {topic}")
                scene.setdefault("on_screen_text", "")
            while len(data["scenes"]) < min_scenes:
                data["scenes"].append({
                    "narration": "This story still shapes how we understand the world today.",
                    "image_prompt": f"realistic detailed illustration related to {topic}",
                    "on_screen_text": "Still Relevant Today"
                })
            data.setdefault("title_variants", [f"The Wild True Story Behind This"])
            data.setdefault("description", f"The surprising true story: {topic}.")
            data.setdefault("thumbnail_text", "TRUE STORY")
            data.setdefault("company", topic)
            data.setdefault("hashtags", ["#shorts", "#facts", "#truestory"])
            data.setdefault("seo_tags", ["history", "facts", "true story"])
            print(f"      [OK] Story script generated: {len(data['scenes'])} scenes")
            return data
    except Exception as e:
        print(f"      [!] Story API Error: {e}")

    print("      [!] Using dynamic story fallback...")
    fallback_scenes = [
        {"narration": f"Here is a true story: {topic}.", "image_prompt": f"realistic illustration depicting {topic}", "on_screen_text": topic[:30]},
        {"narration": f"Most people have never heard the full story behind {topic}.", "image_prompt": f"realistic illustration, early events of {topic}", "on_screen_text": "The Untold Story"},
        {"narration": f"{topic} unfolded in a way nobody expected at the time.", "image_prompt": f"realistic dramatic illustration of {topic} unfolding", "on_screen_text": "How It Happened"},
        {"narration": f"The details of {topic} are stranger than most people realize.", "image_prompt": f"realistic illustration, key moment of {topic}", "on_screen_text": "The Surprising Details"},
        {"narration": f"Historians still study {topic} because of how unusual it was.", "image_prompt": f"realistic illustration, historians examining {topic}", "on_screen_text": "Still Studied Today"},
        {"narration": f"The effects of {topic} can still be seen in the world today.", "image_prompt": f"realistic illustration, modern-day connection to {topic}", "on_screen_text": "Still Felt Today"},
        {"narration": f"{topic} remains one of the strangest true stories in history.", "image_prompt": f"realistic illustration, closing scene of {topic}", "on_screen_text": "A True Story"},
    ]
    return {
        "title_variants": [f"{topic}"[:95]],
        "description": f"The surprising true story: {topic}.",
        "thumbnail_text": "TRUE STORY",
        "company": topic,
        "hashtags": ["#shorts", "#facts", "#truestory"],
        "seo_tags": ["history", "facts", "true story"],
        "scenes": fallback_scenes[:min_scenes] if video_type != "long" else fallback_scenes
    }


def generate_comparison_script(a, b, video_type="short", **kwargs):
    return generate_invention_script(f"{a} vs {b}", "Unknown", "", "", video_type)


def generate_listicle_script(topic, video_type="short"):
    """Generates a numbered listicle script. Each entry becomes one scene:
    a real name, their key contribution, and a portrait-style image."""
    num_entries = 8 if video_type == "long" else 5

    prompt = f"""Create a numbered listicle video script about: {topic}.
Pick {num_entries} real, specific, well-known entries (people, places, or things depending on the topic).
For each entry, write ONE spoken narration sentence introducing them and their key contribution or fact
(natural spoken style, no scene numbers spoken aloud), plus a short 2-4 word on-screen label,
plus an image_prompt describing that specific entry (their portrait or the specific object) for a cartoon illustration.

Return ONLY valid JSON in EXACTLY this structure:
{{
  "title_variants": ["title using a number", "title using curiosity gap", "title using contradiction"],
  "description": "short video description",
  "thumbnail_text": "short punchy thumbnail text",
  "hashtags": ["#shorts", "#facts"],
  "seo_tags": ["tag1", "tag2"],
  "scenes": [
    {{"entry_name": "Real name of person or thing", "narration": "one sentence introducing them and their key contribution", "image_prompt": "portrait or object description for cartoon illustration of this specific entry", "on_screen_text": "Name or short label"}}
  ]
}}

Include exactly {num_entries} scenes, one per entry, each with a DIFFERENT real name or subject."""

    for attempt in range(2):
        try:
            print(f"      Calling Groq API for listicle (attempt {attempt+1}/2)...")
            resp = requests.post(GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.8, "response_format": {"type": "json_object"}},
                timeout=120)
            resp_data = resp.json()
            if "choices" in resp_data and len(resp_data["choices"]) > 0:
                data = json.loads(resp_data["choices"][0]["message"]["content"])
                data.setdefault("scenes", [])
                for idx, scene in enumerate(data["scenes"]):
                    scene.setdefault("entry_name", topic)
                    scene.setdefault("narration", f"Here is another key fact about {topic}.")
                    scene.setdefault("image_prompt", f"cartoon illustration related to {topic}, entry {idx+1}")
                    scene.setdefault("on_screen_text", scene.get("entry_name", ""))
                data.setdefault("title_variants", [f"{num_entries} Things You Didn't Know About {topic}"])
                data.setdefault("description", f"A countdown of {topic}.")
                data.setdefault("thumbnail_text", "DID YOU KNOW?")
                data.setdefault("company", topic)
                data.setdefault("hashtags", ["#shorts", "#facts", "#listicle"])
                data.setdefault("seo_tags", [topic, "facts", "list"])
                print(f"      [OK] Listicle script generated: {len(data['scenes'])} entries")
                return data
            else:
                print(f"      [!] Listicle attempt {attempt+1} returned no choices")
        except Exception as e:
            print(f"      [!] Listicle API Error (attempt {attempt+1}): {e}")

    print("      [!] Using dynamic listicle fallback...")
    return {
        "title_variants": [f"{num_entries} Things About {topic}"],
        "description": f"A countdown about {topic}.",
        "thumbnail_text": "DID YOU KNOW?",
        "company": topic,
        "hashtags": ["#shorts", "#facts", "#listicle"],
        "seo_tags": [topic, "facts", "list"],
        "scenes": [
            {"entry_name": f"{topic} fact {i+1}", "narration": f"Here is fact number {i+1} about {topic}.",
             "image_prompt": f"cartoon illustration related to {topic}", "on_screen_text": f"Fact {i+1}"}
            for i in range(num_entries)
        ]
    }
