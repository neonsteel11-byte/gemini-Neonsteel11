import os
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def human_polish_engine(raw_script, video_type="long"):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # The ultimate human-creator critique prompt
    critique_prompt = f"""
    You are a cynical, highly successful YouTube Director specializing in financial roasts. 
    Review the raw script below and completely rewrite it to sound like a native English-speaking human creator.
    
    CRITICAL HUMAN CRITERIA:
    1. Ban all AI tropes: Ban words like 'delve', 'testament', 'beacon', 'revolutionize', 'moreover', or 'in conclusion'.
    2. Add comedic timing: Insert sarcastic pauses, rhetorical questions to the audience, and sharp, punchy modern slang.
    3. Pacing check: Ensure sentences are short and punchy so the voice actor doesn't sound out of breath.
    4. Target Length: Keep it strictly matching a {video_type} format structure.
    
    Raw Script:
    {raw_script}
    """
    
    response = model.generate_content(critique_prompt)
    return response.text

print("📝 Script Polish Engine initialized successfully.")
