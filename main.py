import os
import sys
import subprocess
from google import genai
from google.genai import types

def run_stage(command, description):
    """Executes a pipeline stage and captures output."""
    print(f"⚙️ [Pipeline]: Running {description}...")
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result

def consult_ai_ceo_for_fix(script_name, error_log):
    """Wakes up the AI CEO, hands it the error log, and demands a code patch."""
    print("👑 [AI CEO]: Critical operational bottleneck detected. Reviewing logs...")
    
    # Initialize the Gemini Client (using the official google-genai SDK)
    client = genai.Client()
    
    # Read the broken script to give the CEO full context
    with open(script_name, "r") as f:
        broken_code = f.read()

    prompt = f"""
    You are the Autonomous AI CEO of this automated YouTube factory. 
    The pre-upload validation guard has BLOCKED the deployment because your visual engine generated a broken or unreadable video file.
    
    TARGET SCRIPT TO FIX:
    ```{script_name}
    {broken_code}
    ```
    
    CRITICAL RUNTIME ERROR LOG:
    {error_log}
    
    TASK:
    Analyze what went wrong. Rewrite the entire contents of {script_name} so that it successfully outputs real, fully-encoded, high-retention MP4 videos that will pass the OpenCV frame integrity verification.
    
    OUTPUT RULE:
    Return ONLY the raw python code. Do not wrap it in markdown block quotes, do not include chat prose. Your output must be directly executable.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    # Overwrite the broken script with the CEO's executive command patch
    fixed_code = response.text.strip().replace("```python", "").replace("```", "")
    with open(script_name, "w") as f:
        f.write(fixed_code)
    
    print(f"🔧 [AI CEO]: Executive patch successfully compiled and deployed to {script_name}.")

def main():
    print("👑 [AI CEO]: Initializing Autonomous Executive Management System...")
    company_target = "Airbnb"
    
    # Maximum fix attempts before throwing a hard exception
    max_healing_loops = 3
    
    for attempt in range(1, max_healing_loops + 1):
        print(f"\n🔄 [Iteration {attempt}]: Executing visual manufacturing layout...")
        
        # 1. Compile the frames
        run_stage(f"python scripts/visual_composer.py {company_target}", "Visual Frame Generation")
        
        # 2. Check integrity using the safety script
        validation = run_stage("python scripts/validate_and_upload.py", "Pre-Upload Integrity Sweep")
        
        if validation.returncode == 0:
            print("🛡️ [Pipeline]: Integrity check passed flawlessly!")
            break
        else:
            print(f"🚨 [Pipeline]: Safety Guard triggered an alert on attempt {attempt}!")
            if attempt == max_healing_loops:
                print("💀 [Pipeline]: Self-healing thresholds exceeded. Hard crashing to protect channel state.")
                sys.exit(1)
            
            # Combine stdout and stderr for the CEO to read
            combined_logs = validation.stdout + "\n" + validation.stderr
            consult_ai_ceo_for_fix("scripts/visual_composer.py", combined_logs)

    # 3. Final Execution Report Delivered directly to your desk (Console logs)
    print("\n=======================================================")
    print("📊 FINAL EXECUTIVE DESK REPORT - HEAD OF PIPELINE")
    print("=======================================================")
    print(f"✅ Production Status: SUCCESSFUL")
    print(f"🎬 Target Commodity: {company_target}")
    print(f"🛡️ Safety Verification: PASS")
    print("🚀 Action: Broadcast stream launched to YouTube Studio on autopilot.")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
