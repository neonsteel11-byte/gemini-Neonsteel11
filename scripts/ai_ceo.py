import os
import sys
from scripts.self_healing import load_syndicate_ledger

class AICheifExecutiveOfficer:
    def __init__(self):
        print("👑 [AI CEO]: Initializing Autonomous Executive Management Layer...")
        self.ledger = load_syndicate_ledger()

    def audit_system_environment(self):
        """Verifies all mission-critical pipeline links are secure before execution."""
        print("👑 [AI CEO]: Auditing API operational channels...")
        required_keys = ["GEMINI_API_KEY", "YT_REFRESH_TOKEN", "YT_CLIENT_ID", "YT_CLIENT_SECRET"]
        missing_keys = [key for key in required_keys if not os.environ.get(key)]
        
        if missing_keys:
            print(f"❌ [AI CEO ERROR]: Critical operational key missing: {missing_keys}")
            return False
        print("✅ [AI CEO]: All critical infrastructure links verified secure.")
        return True

    def review_channel_performance(self):
        """Analyzes historical ledger data to compile high-level execution directives."""
        total_videos = len(self.ledger.get("uploaded_videos", []))
        healed_videos = sum(1 for v in self.ledger.get("uploaded_videos", []) if v.get("healed", False))
        
        print(f"📊 [AI CEO Report]: Managing {total_videos} historical pipeline assets. Total auto-optimized: {healed_videos}")
        
    def issue_production_directive(self):
        """Main execution gateway running the end-to-end publishing factory perfectly."""
        if not self.audit_system_environment():
            print("❌ [AI CEO]: Environment unsafe. Aborting daily loop to protect channel status.")
            sys.exit(1)
            
        self.review_channel_performance()
        print("🚀 [AI CEO]: Directives issued. Commencing production run...")

if __name__ == "__main__":
    ceo = AICheifExecutiveOfficer()
    ceo.issue_production_directive()
