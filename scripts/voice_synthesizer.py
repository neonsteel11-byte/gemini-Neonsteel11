import os
import asyncio
import edge_tts

async def synthesize_narration_audio(text_script, output_audio_path, voice="en-US-ChristopherNeural"):
    """
    Converts raw text scripts into sharp, high-retention audio narratives.
    """
    print(f"🎙️ [Voice Synthesizer]: Rendering high-retention human audio track using {voice}...")
    
    # Ensure the output directory structure is initialized
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)
    
    # Clean the script text of any lingering markdown artifacts or structural notes
    clean_text = text_script.replace("**", "").replace("*", "").replace("###", "").strip()
    
    communicate = edge_tts.Communicate(clean_text, voice)
    await communicate.save(output_audio_path)
    print(f"✅ Audio asset successfully saved to disk: {output_audio_path}")

if __name__ == "__main__":
    # Test execution block
    sample_text = "This is a live test of the high-revenue automated finance channel framework."
    asyncio.run(synthesize_narration_audio(sample_text, "output/test_voice.mp3"))
