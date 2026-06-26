import os
from moviepy.editor import ColorClip, AudioFileClip, CompositeVideoClip, TextClip
from gtts import gTTS
from pathlib import Path

def text_to_speech(text, out_path):
    tts = gTTS(text)
    tts.save(out_path)
    return out_path

def compose(video_file_path, script_text, thumbnail_path=None, duration=45):
    Path(os.path.dirname(video_file_path)).mkdir(parents=True, exist_ok=True)
    audio_path = video_file_path.replace(".mp4", ".mp3")
    text_to_speech(script_text, audio_path)
    
    audioclip = AudioFileClip(audio_path)
    real_duration = audioclip.duration
    
    bg = ColorClip((1280, 720), color=(25, 25, 25), duration=real_duration)
    
    txt = TextClip(script_text, fontsize=32, color='white', method='caption', size=(1100, None)).set_position("center")
    txt = txt.set_start(0).set_duration(real_duration)
    
    final = CompositeVideoClip([bg, txt]).set_duration(real_duration)
    final = final.set_audio(audioclip)
    
    final.write_videofile(video_file_path, fps=24, codec="libx262" if os.name == 'nt' else "libx264", audio_codec="aac", threads=2)
    
    if thumbnail_path:
        Path(os.path.dirname(thumbnail_path)).mkdir(parents=True, exist_ok=True)
        final.save_frame(thumbnail_path, t=1.0)
    
    # Clean up audio file
    audioclip.close()
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return video_file_path