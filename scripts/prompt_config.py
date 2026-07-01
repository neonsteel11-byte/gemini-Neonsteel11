def get_advanced_roast_prompt(company_name, fresh_trends, video_type='short'):
    if video_type.lower() == 'short':
        word_count_rule = "STRICTLY between 90 and 110 words total. Do not exceed this limit under any circumstance."
        pacing_rule = "Rapid, high-energy 3-second scene cuts. Designed for instant hooks and immediate retention."
        format_style = "Vertical 9:16 layout formatting directions."
    else:
        # Long-form configurations (8-10 minute sweet spot for mid-rolls)
        word_count_rule = "STRICTLY between 1,100 and 1,350 words total. Break the script down cleanly into 5 distinct chapters or sub-topics."
        pacing_rule = "Deep-dive investigative pacing, balancing savage humor with actual deep financial analysis. Paced for a native 8 to 10 minute spoken video."
        format_style = "Horizontal 16:9 cinematic widescreen layout formatting directions, complete with introduction, smooth transitions, mid-video hooks, and an outro."

    return f"""
    You are a lead animator and financial investigative scriptwriter for a high-retention corporate roast channel.
    Analyze the recent performance data and trends for: {company_name}.
    Contextual current event notes: {fresh_trends}

    CRITICAL LENGTH & FORMAT RULES:
    1. VIDEO TYPE: This is a {video_type.upper()} video.
    2. WORD COUNT CONSTRAINT: {word_count_rule}
    3. MOVEMENT & PACING: {pacing_rule}
    4. VISUAL FORMATTING: {format_style}

    GENERAL VISUAL STYLE RULES:
    - Style: Bold, vivid cartoon/comic-book vector illustration style. Use intense cel-shading, vibrant neon-accented business environments, and thick black outlines.
    - No Real Images: Absolutely zero real-world stock imagery or static corporate photos are allowed. Everything must look like an expressive digital animation cell.
    - Kinetic Text: Generate text overlays using bright yellow or green fonts with heavy black borders to maximize Tier 1 mobile and desktop CTR appeal.
    """
