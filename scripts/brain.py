import os
import google.generativeai as genai

def generate_script(headline, context=""):
    # This securely reads the key from GitHub Secrets instead of leaking it
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "No API key config found. Roast skipped."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are a cynical, hilarious corporate satirist and tech comedy creator. 
    Write a 120-140 word spoken video script (~45 seconds) that ruthlessly roasts the absolute absurdity 
    of the big company, billionaire executive, or tech industry news item provided below.

    STYLE GUIDELINES:
    - Tone: Sharply sarcastic, biting, corporate-cynical, and punchy. Think "Silicon Valley" or corporate TikTok.
    - Focus: Make fun of corporate buzzwords, terrible pivot strategies, massive PR disasters, and out-of-touch CEOs.
    - Structure: Use short, snappy sentences, sarcastic one-liners, and comedic timing. Do NOT talk like a financial advisor. 
    - End with this exact sentence: "Subscribe for more corporate burns."

    Headline: "{headline}"
    Context: "{context}"
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to generate roast due to error: {e}"
