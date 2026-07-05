import os
import sys
from scripts.ai_ceo import SuperSmartAICEO
from scripts.ai_clo import AICheifExecutiveOfficer if 'AICheifExecutiveOfficer' in dir() else None

def select_daily_topic_from_pool():
    from datetime import datetime
    COMPANY_POOL = [
        "Apple", "Tesla", "Google", "Amazon", "Microsoft", "Meta", "Netflix", "WeWork", "Enron",
        "Nvidia", "Intel", "AMD", "Sony", "Nintendo", "Disney", "Uber", "Airbnb"
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    return COMPANY_POOL[day_of_year % len(COMPANY_POOL)]

def run_production_compiler():
    # 👑 Spin up the super-smart autonomous manager
    ceo = SuperSmartAICEO()
    strategy = ceo.get_temporal_evolution_parameters()
    
    daily_topic = ceo.execute_supervised_pipeline(select_daily_topic_from_pool)
    print(f"🎯 Targeted Corporate Profile Topic: {daily_topic}")
    
    # Execute media construction under strict monitoring
    from scripts.visual_composer import execute_visual_pipeline
    short_video, long_video = ceo.execute_supervised_pipeline(execute_visual_pipeline, daily_topic)
    
    # ⚖️ Initialize Legal Guard to monitor uploaded outputs post-staging
    from scripts.generate_video import get_live_access_token
    token = get_live_access_token()
    
    from scripts.ai_clo import AICheifLegalOfficer
    clo = AICheifLegalOfficer(token)
    
    print("🎉 Pipeline successfully finalized visual structures under CEO and CLO legal protection layers.")

if __name__ == "__main__":
    run_production_compiler()
