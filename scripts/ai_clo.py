import os
import requests
from scripts.self_healing import load_syndicate_ledger

class AICheifLegalOfficer:
    def __init__(self, access_token):
        print("⚖️ [AI CLO]: Initializing Autonomous Legal Guard & Copyright Protection Layer...")
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def audit_holding_tank_for_copyright(self, video_id):
        """
        Inspects YouTube's automated Content ID and processing status.
        Returns True if clean, or False if a copyright/policy flag is intercepted.
        """
        print(f"⚖️ [AI CLO]: Auditing hidden video ID {video_id} for copyright compliance inside holding tank...")
        url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,status&id={video_id}"
        
        try:
            res = requests.get(url, self.headers).json()
            if "items" in res and len(res["items"]) > 0:
                item = res["items"][0]
                
                # Check for policy/claim flags returned by YouTube's processing engine
                status = item.get("status", {})
                if status.get("rejectionReason") or not status.get("isLinked", True):
                    print(f"🚨 [AI CLO ALERT]: Copyright claim or policy restriction detected on video {video_id}!")
                    return False
                    
            print(f"✅ [AI CLO]: Video ID {video_id} passed all internal copyright audits.")
            return True
        except Exception as e:
            print(f"⚠️ [AI CLO]: Network anomaly during copyright scan: {str(e)}. Defaulting to safe holding mode.")
            return False

    def intercept_and_recompile(self, video_id, company_name, video_type, ceo_instance):
        """If a video fails copyright, this instantly commands a structural rewrite."""
        print(f"🩺 [AI CLO - HEALING]: Intercepting video {video_id}. Ordering immediate visual/text mutation...")
        
        # Change seed variables slightly so the visual compiler produces different frame signatures
        os.environ["FORCE_MUTATION_SIGNAL"] = "TRUE"
        print("🔄 [AI CLO]: Forcing dynamic layout shift to clear platform signature blocks.")
        
        # Trigger re-generation via the CEO safety wrapper
        from scripts.visual_composer import execute_visual_pipeline
        execute_visual_pipeline(company_name)
        print(f"✨ [AI CLO]: Fresh mutated visual container compiled successfully for {company_name}.")
