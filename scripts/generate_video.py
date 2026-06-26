#!/usr/bin/env python3
import os
import json
import urllib.request
import google.generativeai as genai
from elevenlabs.client import ElevenLabs

# Secure API Configurations
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize ElevenLabs Client
elevenlabs_client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

def get_ai_metadata(topic):
    """Asks Gemini to create a viral YouTube title and description."""
    prompt = f"Create a viral corporate satire YouTube title and description for a video about: {topic}. Return ONLY JSON format like: {{\"title\": \"...\", \"description\": \"...\"}}"
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"AI failed to generate metadata: {e}. Using default.")
        return {"title": f"The Corporate Breakdown of {topic}", "description": "Automated reality check via Syndicate Bot."}

def generate_human_voiceover(text, output_audio_path):
    """Converts the satirical script into highly-realistic human audio."""
    print("-> Connecting to ElevenLabs for human voice synthesis...")
    try:
        audio_data = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb", # George - Excellent cynical/punchy voice profile
            model_id="eleven_v3",
            output_format="mp3_44100_128"
        )
        
        # Save the audio stream chunk data safely
        with open(output_audio_path, "wb") as f:
            for chunk in audio_data:
                if chunk:
                    f.write(chunk)
        print(f"-> Human voice audio generated successfully at: {output_audio_path}")
        return True
    except Exception as e:
        print(f"ElevenLabs voice synthesis failed: {e}")
        return False

def generate_autonomous_media():
    os.makedirs("output", exist_ok=True)
    video_id = f"vid_{os.urandom(4).hex()}"
    video_path = f"output/{video_id}.mp4"
    audio_path = f"output/{video_id}.mp3"

    # 1. Simulate/Download template base video asset
    if not os.path.exists(video_path):
        print(f"-> Fetching video template framework for {video_id}...")
        urllib.request.urlretrieve("https://www.w3schools.com/html/mov_bbb.mp4", video_path)

    # 2. Extract context from latest headline inside manifest
    manifest_path = "output/manifest.json"
    headline = "Big Tech Corporate Realities"
    script_text = "Welcome to another corporate burn. Subscribe for more corporate burns."
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                current_manifest = json.load(f)
                headline = current_manifest.get("headline", headline)
        except Exception:
            pass

    # 3. Generate human narrative audio from the underlying script
    # (Assuming your script runner pipeline feeds generated text cleanly)
    generate_human_voiceover(script_text, audio_path)

    # 4. Fetch dynamic, viral video presentation details
    metadata = get_ai_metadata(headline)

    # 5. Reload and update the system configuration ledger
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    else:
        manifest = {"videos": []}

    # 6. Structuring structural video entries
    new_video = {
        "id": video_id,
        "status": "pending",
        "file_path": video_path,
        "audio_path": audio_path,
        "title": metadata["title"],
        "description": metadata["description"],
        "categoryId": "23" # Comedy Category ID mapping
    }

    if "videos" not in manifest:
        manifest["videos"] = []
        
    manifest["videos"].append(new_video)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"-> Generation complete. Manifest updated to human track: {metadata['title']}")

if __name__ == "__main__":
    generate_autonomous_media()
