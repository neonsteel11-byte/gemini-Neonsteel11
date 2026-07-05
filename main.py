import os
import sys
from scripts.ai_ceo import SuperSmartAICEO
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
    # 👑 Spin up the super-smart autonomous manager
    ceo = SuperSmartAICEO()
    
    # Analyze global chronological vectors
    strategy = ceo.get_temporal_evolution_parameters()
    
    # Safely select topic under supervisor oversight
    daily_topic = ceo.execute_supervised_pipeline(select_daily_topic_from_pool)
    print(f"🎯 Targeted Corporate Profile Topic: {daily_topic}")
    
    # Execute media construction inside the self-healing loop
    print(f"🎬 Compiling visual assets using {strategy['style_era']} guidelines...")
    short_video, long_video = ceo.execute_supervised_pipeline(execute_visual_pipeline, daily_topic)
    
    print("🎉 Pipeline successfully executed all instructions under AI CEO monitoring.")

if __name__ == "__main__":
    run_production_compiler()
