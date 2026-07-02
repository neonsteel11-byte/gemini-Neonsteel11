import os
import google.generativeai as genai

# Configure Gemini using your secure repository environment keys
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class HumanDirectorSuite:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def trend_jack_modifier(self, company_name):
        """Simulates a human browsing social media for recent angles."""
        print(f"🔥 [1/3 Trend-Jacking]: Injecting modern cultural angle for {company_name}...")
        # In a full production build, this connects to live RSS or scraping feeds.
        # For now, it forces Gemini to find a hilarious, pop-culture angle instead of dry history.
        return f"Focus heavily on the most chaotic, meme-worthy executive decisions and recent public backlashes regarding {company_name}."

    def generate_high_retention_opener(self, company_name):
        """Creates a high-drama 5-second human style visual hook."""
        print(f"🪝 [2/3 Retention Hook]: Crafting an aggressive, high-retention opening scene...")
        prompt = f"Write a shocking, 1-sentence opening line for a video roasting {company_name}. No greetings, no intro music cues. Start with pure drama."
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def self_correction_polish_loop(self, raw_script, video_type):
        """The Editorial Polish Loop: Rewrites the script to kill robotic AI filler words."""
        print(f"📝 [3/3 Self-Correction]: Reviewing script through the Editor Loop...")
        critique_prompt = f"""
        You are an elite, cynical YouTube Director. Rewrite this raw script segment to sound like a native English-speaking human.
        
        STRICT RULES:
        1. Delete all AI tropes entirely: Never use words like 'delve', 'testament', 'beacon', 'revolutionize', 'moreover', 'furthermore', or 'in conclusion'.
        2. Sentence Structure: Break long phrases into short, punchy, rhythmic sentences.
        3. Tone: Add subtle, deadpan sarcasm and rhetorical questions directly to the audience.
        
        Format: {video_type.upper()} video style.
        Raw Script text: {raw_script}
        """
        response = self.model.generate_content(critique_prompt)
        return response.text.strip()

    def process_complete_human_workflow(self, company_name, video_type="short"):
        print(f"\n🎬 Starting Human Director workflow for: {company_name.upper()} ({video_type.upper()})")
        
        # 1. Trend angle modifier
        trend_angle = self.trend_jack_modifier(company_name)
        
        # 2. Build Hook
        hook = self.generate_high_retention_opener(company_name)
        print(f"   ↳ Hook Generated: \"{hook}\"")
        
        # 3. Simulate raw content generation and run the Editorial Polish
        raw_placeholder_body = f"This is a breakdown of {company_name}. They made a series of business updates. {trend_angle}"
        final_polished_script = self.self_correction_polish_loop(f"{hook} {raw_placeholder_body}", video_type)
        
        print(f"✨ Final Human-Polished Script Ready for Voiceover Engine!")
        return final_polished_script

if __name__ == "__main__":
    director = HumanDirectorSuite()
    # Quick live test execution on a premium corporate target
    director.process_complete_human_workflow("WeWork", video_type="short")
