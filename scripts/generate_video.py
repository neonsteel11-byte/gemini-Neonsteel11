import os
import sys
import requests
from google import genai
from gtts import gTTS
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

from moviepy import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip, ImageClip

def fetch_latest_finance_news():
    print("Fetching live corporate finance headlines...")
    api_key = os.environ.get("NEWS_API_KEY", "253c5bc3faba48628fc74e2c717bb165")
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={api_key}"
    
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])
        headlines = [a["title"] for a in articles[:10] if a.get("title")]
        return "\n".join(headlines) if headlines else "General tech layoffs and market corporate trouble."
    except Exception as e:
        print(f"Failed to fetch live news, using backup context: {e}")
        return "Big tech corporate struggles and market volatility."

def generate_roast_script(news_context):
    print("Handing headlines to Gemini to compile a roast script...")
    client = genai.Client()
    
    prompt = f"""
    Analyze these latest business news headlines:
    {news_context}
    
    Pick one company mentioned or relevant to these struggles (e.g., a massive tech or finance entity making bad decisions, losing money, or doing layoffs).
    Write a highly engaging, sarcastic 30-second narration roasting their financial scenario.
    Make it punchy and optimized for a viral YouTube short. 
    Provide ONLY the spoken narration text. No stage descriptions, no brackets, no extra fluff.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text.strip()

def upload_to_youtube(video_path, title, description):
    print("Initializing automated cloud upload to YouTube...")
    try:
        creds = google.oauth2.credentials.Credentials(
            token=None,
            refresh_token=os.environ.get("YT_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("YT_CLIENT_ID"),
            client_secret=os.environ.get("YT_CLIENT_SECRET")
        )
        
        youtube = build("youtube", "v3", credentials=creds)
        
        request_body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": ["finance", "roast", "shorts", "business"],
                "categoryId": "25" # News & Politics
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        upload_request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
        
        print(f"Uploading {video_path}...")
        response = upload_request.execute()
        print(f"🚀 Success! Video uploaded. Video ID: {response.get('id')}")
    except Exception as e:
        print(f"❌ YouTube Upload failed: {e}")

def create_automated_video(output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Fetch news and construct script via Gemini
    news_headlines = fetch_latest_finance_news()
    roast_text = generate_roast_script(news_headlines)
    print(f"\nFinal AI Script Draft:\n\"{roast_text}\"\n")
    
    # 2. Text-to-Speech
    tts_path = os.path.join(output_dir, "voiceover.mp3")
    tts = gTTS(text=roast_text, lang='en', tld='com')
    tts.save(tts_path)
    
    # 3. Assemble Visual Timeline
    audio_clip = AudioFileClip(tts_path)
    total_duration = audio_clip.duration
    
    clips = []
    base_image = "assets/images/scene1_bed.png"
    if os.path.exists(base_image):
        base_clip = ImageClip(base_image).with_duration(total_duration)
    else:
        base_clip = ColorClip(size=(1920, 1080), color=(25, 20, 30)).with_duration(total_duration)
        
    clips.append(base_clip.with_start(0).with_position("center"))
    
    video_asset = "assets/videos/clip_5s.mp4"
    if os.path.exists(video_asset) and total_duration > 7:
        overlay_video = VideoFileClip(video_asset).with_duration(5.0).without_audio()
        clips.append(overlay_video.with_start(3.0).with_position("center"))
        
    canvas = CompositeVideoClip(clips, size=(1920, 1080)).with_duration(total_duration)
    final_video = canvas.with_audio(audio_clip)
    
    # 4. Render vertical Shorts layout
    short_video_path = os.path.join(output_dir, "final_short.mp4")
    short_w = int(1080 * (9/16))
    x1 = int((1920 - short_w) / 2)
    short_video = final_video.cropped(x1=x1, y1=0, width=short_w, height=1080)
    
    print("Rendering vertical Shorts package...")
    short_video.write_videofile(short_video_path, fps=24, codec="libx264", audio_codec="aac")
    audio_clip.close()
    
    # 5. Push production asset live to YouTube Shorts channel
    upload_to_youtube(
        video_path=short_video_path,
        title="Corporate Finance Gets Destroyed 😂 #shorts",
        description=f"Today's financial breakdown:\n{roast_text}\n\nGenerated automatically via pipeline."
    )

if __name__ == "__main__":
    create_automated_video()
