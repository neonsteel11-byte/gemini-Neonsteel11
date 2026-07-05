import os
import sys
import subprocess

def run_stage(command, description):
    """Executes an internal pipeline sequence cleanly."""
    print(f"⚙️ [VISION Core]: Executing {description}...")
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"❌ [Error in {description}]:\n{result.stderr}\n{result.stdout}")
    return result

def main():
    print("🤖 [SYSTEM]: Activating Stable VISION Core Production Architecture...")
    company_target = "Airbnb"
    
    # 1. Run the local visual rendering script directly
    build_status = run_stage(f"python scripts/visual_composer.py {company_target}", "Media Synthesis Engine")
    
    if build_status.returncode != 0:
        print("🚨 [VISION Core]: Synthesis failed. Structural halting triggered.")
        sys.exit(1)

    # 🚀 2. Execute the YouTube Data API transmission script directly
    print("🚀 [VISION Core]: Security verification clear. Broadcasting Asset Packages...")
    upload_result = run_stage("python scripts/upload_to_youtube.py", "Broadcasting Asset Packages")

    if upload_result.returncode == 0:
        print("\n" + "="*55)
        print("📊 EXECUTIVE DESK REPORT // PRODUCTION PIPELINE COMPLETE")
        print("="*55 + "\n")

if __name__ == "__main__":
    main()
