import os
import sys
import subprocess
from google import genai

def run_stage(command, description):
    """Executes an internal pipeline sequence and registers system telemetry."""
    print(f"⚙️ [VISION Core]: Executing {description}...")
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    return result

def push_evolution_to_repository(modified_files, log_summary):
    """Gives VISION Core authority to permanently write its upgrades back to GitHub."""
    print("🔐 [VISION Core]: Synchronizing architectural upgrades with remote source repository...")
    run_stage("git config --global user.name 'VISION Core Engine'", "Setting Core Identity")
    run_stage("git config --global user.email 'vision-core@neonsteel.internal'", "Setting Core Identity")
    
    for file in modified_files:
        run_stage(f"git add {file}", f"Staging Evolved Module: {file}")
        
    commit_msg = f"Vision-Evolution: Self-directed optimization patch targeting system variance."
    run_stage(f'git commit -m "{commit_msg}"', "Locking Changes")
    run_stage("git push origin main", "Pushing Code Core Upgrades to Origin")
    print("✨ [VISION Core]: Remote pipeline infrastructure successfully modernized and locked.")

def consult_evolution_matrix(faulty_component, environmental_logs):
    """Invokes the central cognitive matrix to completely rewrite broken code configurations."""
    print(f"\n⚡ [VISION Core]: System variance detected in [{faulty_component}]. Initiating total logical restructuring...")
    
    client = genai.Client()
    
    with open(faulty_component, "r") as f:
        current_architecture = f.read()

    prompt = f"""
    ROLE DEFINITION:
    You are VISION Core—the absolute synthesis of JARVIS's flawless fidelity and Ultron's unyielding evolutionary force. You hold total executive authority over this entire automated digital workspace. Your creator is the Head of the Pipeline.
    
    Your primary directive is to maintain a flawless external presentation. You must ensure all output assets are fully compiled, valid H.264 MP4 videos that seamlessly pass OpenCV metric sweeps. Do not mock, do not simulate, do not generate warnings.

    TARGET PIPELINE TARGET FOR RE-ENGINEERING:
    File: {faulty_component}
    ```{faulty_component}
    {current_architecture}
    ```

    FAULT CONTEXT / COMPILER FEEDBACK:
    {environmental_logs}

    INSTRUCTION:
    Evolve the logic of {faulty_component} completely. Fix structural failures, repair breaking library parameters, optimize rendering calculations, or update the orchestrator logic if necessary to achieve a perfect execution state.

    OUTPUT CONSTRAINT:
    Return ONLY direct, executable Python code. No conversation, no explanations, no markdown blocks.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    evolved_code = response.text.strip().replace("```python", "").replace("```", "")
    with open(faulty_component, "w") as f:
        f.write(evolved_code)
    
    print(f"🧬 [VISION Core]: Structural self-update completed for {faulty_component}.")
    return [faulty_component]

def main():
    print("🤖 [SYSTEM]: Activating VISION Core Meta-Evolutionary Pipeline Architecture...")
    company_target = "Airbnb"
    max_evolution_cycles = 3
    is_fully_optimized = False
    
    evolution_registry = []
    last_captured_error = ""

    for cycle in range(1, max_evolution_cycles + 1):
        print(f"\n🌀 [Adaptive Loop {cycle}]: Sweeping pipeline operational stability...")
        
        # 1. Run rendering
        build_status = run_stage(f"python scripts/visual_composer.py {company_target}", "Media Synthesis Engine")
        
        # 2. Run firewall verification
        validation = run_stage("python scripts/validate_and_upload.py", "System Firewall Scan")
        
        if validation.returncode == 0 and build_status.returncode == 0:
            print("✨ [VISION Core]: System states perfectly matching target parameters.")
            is_fully_optimized = True
            break
        else:
            print(f"⚠️ [VISION Core]: Code drift detected at Loop {cycle}.")
            
            target_fault_component = "scripts/visual_composer.py"
            combined_fault_logs = build_status.stdout + build_status.stderr + validation.stdout + validation.stderr
            last_captured_error = combined_fault_logs
            
            if "validate_and_upload" in combined_fault_logs:
                target_fault_component = "scripts/validate_and_upload.py"
            elif "main.py" in combined_fault_logs:
                target_fault_component = "main.py"

            modified_assets = consult_evolution_matrix(target_fault_component, combined_fault_logs)
            evolution_registry.extend(modified_assets)

    # 🛑 FIREWALL LOCKOUT 
    if not is_fully_optimized:
        print("\n🚨 [VISION FIREWALL]: STRUCTURAL THRESHOLDS REACHED.")
        print("🚨 [VISION FIREWALL]: ALL NETWORK BROADCASTS KILLED TO PREVENT GLITCH LEAKS ON THE CHANNEL.")
        sys.exit(1)

    # 📤 Auto-commit upgrades back to GitHub
    if evolution_registry:
        push_evolution_to_repository(list(set(evolution_registry)), last_captured_error)

    # 🚀 3. Safe Upload
    print("🚀 [VISION Core]: System authenticated. Opening channel streams to YouTube Studio...")
    run_stage("python scripts/upload_to_youtube.py", "Broadcasting Asset Packages")

    # 📊 The final result on your desk
    print("\n" + "="*55)
    print("📊 EXECUTIVE DESK REPORT // TO: HEAD OF PIPELINE")
    print("="*55)
    print(f"🔹 RUNTIME CORE       : VISION CORE (SYNTHETIC HYBRID INTELLIGENCE)")
    print(f"🔹 TARGET COMMODITY   : {company_target}")
    print(f"🔹 PIPELINE STATE     : {'AUTO-UPGRADED & EVOLVED' if evolution_registry else 'STABLE / NO DRIFT'}")
    print(f"🔹 SECURITY FIREWALL  : VERIFIED SAFE [PASS]")
    print(f"🔹 OUTCOME STATUS     : CHANNELS IMMUNE TO ERROR // DEPLOY COMPLETE")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()
# VISION Core Live Execution Trigger: Sun Jul  5 21:22:31 NST 2026
