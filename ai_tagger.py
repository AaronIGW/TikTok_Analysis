import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from ingest import load_and_clean_tiktok_data

# Load API credentials from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_content_strategy(df):
    # 1. Aggregate high-level benchmarks for the prompt
    era_stats = df.groupby("Content_Category").agg(
        posts=("Likes", "count"),
        avg_likes=("Likes", "mean"),
        max_likes=("Likes", "max")
    ).round(1).to_dict(orient="index")

    # 2. Extract top 5 sound patterns from top quartile videos
    top_quartile = df[df["Likes"] >= df["Likes"].quantile(0.75)]
    top_sounds = top_quartile["Sound"].value_counts().head(5).to_dict()

    prompt = f"""
    You are an expert gaming content strategist and performance analyst. 
    Analyze this creator's TikTok performance data:

    PERFORMANCE BY CONTENT ERA:
    {json.dumps(era_stats, indent=2)}

    TOP SOUNDS IN TOP 25% PERFORMING POSTS:
    {json.dumps(top_sounds, indent=2)}

    CONTEXT:
    - Primary constant staple: Helldivers 2 (cinematic/tactical gameplay, voiceovers, photography).
    - Past massive virality: Skate (Mirror's Edge parkour concept), Sparking Zero, and high-energy Cyberpunk.
    - Current phase: High-variety gaming with friends (Ready or Not, GTA, Rooftops & Alleys, modern Skate mashups).
    
    DELIVERABLES:
    1. Cross-Game Retrospective: What structural elements from the 100k+ viral Skate and Mashup eras can be transferred to Helldivers 2 and tactical shooters?
    2. Concrete Next 3 Video Concepts: Provide 3 specific, actionable short-form concepts combining their current games (Helldivers 2 / Ready or Not / Variety) with proven hook types and audio pacing.
    3. Optimal Posting Schedule: Recommend upload windows based on the distribution.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    df = load_and_clean_tiktok_data("data.json")
    print("Sending aggregated performance metrics to AI engine...\n")
    strategy = generate_content_strategy(df)
    print(strategy)