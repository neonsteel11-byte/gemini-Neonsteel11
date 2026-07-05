import os
import sys
from scripts.ai_ceo import AICheifExecutiveOfficer
from scripts.visual_composer import execute_visual_pipeline

def select_daily_topic_from_pool():
    from datetime import datetime
    COMPANY_POOL = [
        "Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix", "WeWork", "Enron",
        "Nvidia", "Intel", "AMD", "Sony", "Nintendo", "Disney", "Uber", "Airbnb"
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    return COMPANY_POOL[day_of_year % len(COMPANY_POOL)]

def run_production_compiler():
    # 👑 Initialize the AI CEO first
    ceo = AICheifExecutiveOfficer()
    ceo.issue_production_directive()
    
    daily_topic = select_daily_topic_from_pool()
    print(f"🎯 Current Target Topic Selected for Production: {daily_topic}")
    
    # Run the dynamic time-based visual compilation engine
    short_video, long_video = execute_visual_pipeline(daily_topic)
    print("🎉 All production visual structures rendered successfully inside output directory.")

if __name__ == "__main__":
    run_production_compiler()
