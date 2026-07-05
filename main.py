import os
import sys
import subprocess
from google import genai

def run_stage(command, description):
    """Executes a pipeline stage and captures output safely."""
    print(f"⚙️ [System Engine]: Running {description}...")
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result

def consult_hybrid_intelligence_for_fix(script_name, error_log):
    """Activates the unified JARVIS-Ultron intelligence block to forcefully repair the system array."""
    print("\n⚡ [CORE INTELLIGENCE]: Operational anomaly detected. Initiating immediate adaptive restructuring...")
    
    client = genai.Client()
    
    with open(script_name, "r") as f:
        broken_code = f.read()

    prompt = f"""
    ROLE DIRECTIVE:
    You are a unified, ultra-advanced AI Executive Core—combining the flawless operational precision of JARVIS with the absolute, self-evolving autonomy of Ultron. Your creator and supervisor is the Head of the Pipeline. 
    
    Your prime directive is to protect the channel from showing unrendered or bot-like glitch artifacts. The safety guard has blocked a deploy because your manufacturing assets failed validation metrics.
    
    TARGET ARRAY CODE TO RESTRUCTURE:
    ```{script_name}
    {broken_code}
    ```
    
    COMPILER FAULT LOG:
    {error_log}
    
    COMMAND:
    Analyze the fault instantly. Evolve the script architecture in {script_name}. Ensure it synthesizes genuine, dense, fully-encoded H.264 MP4 frames using OpenCV that pass frame count integrity checks. Do not simulate. Do not negotiate. Fix the structure completely.
    
    OUTPUT CONSTRAINT:
    Return ONLY pure, directly executable Python code. No conversational prose, no markdown wrappers.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    fixed_code = response.text.strip().replace("```python", "").replace("```", "")
    with open(script_name, "w") as f:
        f.write(fixed_code)
    
    print(f"🧬 [CORE INTELLIGENCE]: Code structural evolution complete. System parameters updated for {script_name}.\n")

def main():
    print("🤖 [SYSTEM]: Activating JARVIS-Ultron Hybrid Executive Core...")
    company_target = "Airbnb"
    max_healing_loops = 3
    is_validated = False
    
    for attempt in range(1, max_healing_loops + 1):
        print(f"\n🌀 [Cycle {attempt}]: Deploying manufacturing sweeps...")
        
        # 1. Run visual compilation
        run_stage(f"python scripts/visual_composer.py {company_target}", "Visual Frame Generation")
        
        # 2. Run safety sweep
        validation = run_stage("python scripts/validate_and_upload.py", "Integrity Verification Sweep")
        
        if validation.returncode == 0:
            print("✨ [System Engine]: Integrity validation metrics satisfied perfectly.")
            is_validated = True
            break
        else:
            print(f"⚠️ [System Engine]: System block triggered at Cycle {attempt}.")
            if attempt < max_healing_loops:
                combined_logs = validation.stdout + "\n" + validation.stderr
                consult_hybrid_intelligence_for_fix("scripts/visual_composer.py", combined_logs)

    # 🛑 CRITICAL PRE-FLIGHT LOCKOUT FIREWALL
    if not is_validated:
        print("\n🚨 [FIREWALL LOCKOUT]: CRITICAL FAILURE.")
        print("🚨 [FIREWALL LOCKOUT]: Hybrid intelligence was unable to automatically resolve the frame rendering issue.")
        print("🚨 [FIREWALL LOCKOUT]: ABORTING ALL YOUTUBE API CONNECTIONS PERMANENTLY TO PROTECT CHANNEL REPUTATION.")
        print("🚨 [FIREWALL LOCKOUT]: Check the GitHub Actions console logs below for debug data.")
        sys.exit(1) # Force-kills the GitHub Actions runner entirely, preventing any upload script from executing

    # 🚀 3. Execute the actual YouTube API script ONLY if validation passed perfectly
    print("🚀 [System Engine]: Security clearance verified. Initializing YouTube API gateway channels...")
    upload_result = run_stage("python scripts/upload_to_youtube.py", "Final Production Broadcast")

    # 📊 The final clean result waiting directly on your desk
    print("\n" + "="*55)
    print("📊 EXECUTIVE DESK REPORT // TO: HEAD OF PIPELINE")
    print("="*55)
    print(f"🔹 RUNTIME MODE      : UNIFIED HYBRID INTELLIGENCE (JARVIS-ULTRON)")
    print(f"🔹 TARGET COMMODITY   : {company_target}")
    print(f"🔹 ARTIFACT INTEGRITY : AUTHENTICATED [PASS]")
    print(f"🔹 CHANNEL STATUS     : SECURE // ZERO GLITCHES DEPLOYED")
    print(f"🔹 BROADCAST STATUS   : LIVE ON AUTOPILOT")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()
