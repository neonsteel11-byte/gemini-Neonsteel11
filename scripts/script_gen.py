import json, re, sys, time, requests
from config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_invention_script(invention, inventor, facts, info, video_type="short"):
    length = "100-130 words, 6-7 scenes" if video_type=="short" else "1000 words"
    prompt = f"Write educational script about {invention}. {length}. MUST include: 1) Shock hook 2) Origin story 3) What it is 4) How used today. Facts: {facts}"
    
    # Retry logic for API calls
    for attempt in range(3):
        try:
            print(f"      Calling Groq API (attempt {attempt+1}/3)...")
            resp = requests.post(GROQ_URL, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], 
                      "temperature": 0.9, "response_format": {"type": "json_object"}},
                timeout=60)
            
            if resp.status_code == 200:
                data = json.loads(resp.json()["choices"][0]["message"]["content"])
                
                # Ensure minimum 6 scenes
                while len(data.get("scenes", [])) < 6:
                    data["scenes"].append({
                        "narration": "Today millions use this invention daily in homes, schools, and workplaces worldwide.",
                        "image_prompt": "modern people using invention, cartoon style, bright colors",
                        "on_screen_text": "Used worldwide"
                    })
                
                print(f"      ✓ Script generated: {len(data['scenes'])} scenes")
                return data
            else:
                print(f"      [!] API error: {resp.status_code}")
                time.sleep(2)
                
        except KeyError as e:
            print(f"      [!] API response error: {e}")
            time.sleep(2)
        except Exception as e:
            print(f"      [!] Request failed: {e}")
            time.sleep(2)
    
    # Fallback: Return basic script if API fails completely
    print("      [WARNING] Using fallback script template")
    return {
        "title_variants": [f"The Surprising Truth About {invention} #shorts"],
        "description": f"Discover the hidden history of {invention}",
        "thumbnail_text": "DID YOU KNOW?",
        "company": invention,
        "hashtags": ["#shorts", "#facts", "#education"],
        "seo_tags": [invention, "history", "facts"],
        "scenes": [
            {"narration": f"You see {invention} every single day. But its origin story will shock you.", "image_prompt": "person looking shocked at object, cartoon", "on_screen_text": "You won't believe this"},
            {"narration": "It was invented completely by accident while someone was trying to create something else entirely.", "image_prompt": "laboratory accident scene, cartoon", "on_screen_text": "Total accident"},
            {"narration": "The inventor never expected this would become one of the most important inventions in history.", "image_prompt": "inventor surprised, cartoon", "on_screen_text": "Changed everything"},
            {"narration": "So what exactly is it? It's a revolutionary product that works through a clever and simple mechanism.", "image_prompt": "close-up of invention, cartoon diagram", "on_screen_text": "How it works"},
            {"narration": "Today, billions of people use this invention every single day without even thinking about it.", "image_prompt": "crowd using invention, cartoon", "on_screen_text": "Used worldwide"},
            {"narration": "From a simple mistake to a world-changing invention - that's the power of accidental genius.", "image_prompt": "lightbulb moment, cartoon", "on_screen_text": "Accidental Genius"}
        ]
    }

def generate_script(company, video_type="short", **kwargs):
    return generate_invention_script(company, "Unknown", "", "", video_type)

def generate_money_story_script(topic, facts, video_type="short"):
    return generate_invention_script(topic, "Unknown", facts, "", video_type)

def generate_listicle_script(topic, video_type="short"):
    return generate_invention_script(topic, "Unknown", "", "", video_type)

def generate_comparison_script(a, b, video_type="short", **kwargs):
    return generate_invention_script(f"{a} vs {b}", "Unknown", "", "", video_type)
