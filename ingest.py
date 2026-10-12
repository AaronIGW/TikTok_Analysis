import json
import pandas as pd
import numpy as np

def classify_content_multidim(row):
    post_date = row.get("Date")
    if pd.isna(post_date):
        d = ""
    else:
        d = post_date.strftime("%Y-%m-%d")

    # Combine any surviving text fields
    text = f"{row.get('Title', '')} {row.get('AlternateText', '')} {row.get('Sound', '')}".lower()
    sound = str(row.get("Sound", "")).lower()
    likes = int(row.get("Likes", 0))

    # =========================================================================
    # 1. PRIMARY GAME CLASSIFICATION
    # =========================================================================

    # Explicit Game Mentions in Metadata / Sound
    if any(k in text for k in ["sparking zero", "dragon ball", "budokai"]):
        game = "Dragon Ball: Sparking! ZERO"
    elif any(k in text for k in ["ready or not"]):
        game = "Ready or Not"
    elif any(k in text for k in ["cyberpunk", "2077", "killmonger", "night city", "silverhand"]):
        game = "Cyberpunk 2077"
    elif any(k in text for k in ["gta", "grand theft auto", "los santos"]):
        game = "GTA"
    elif any(k in text for k in ["hell let loose", "hll"]):
        game = "Hell Let Loose"
    elif any(k in text for k in ["dying light", "the beast"]):
        game = "Dying Light: The Beast"
    elif any(k in text for k in ["mirrors edge", "mirror's edge", "parkour"]):
        game = "Skate"
    elif any(k in text for k in [
        "need for speed", "nfs", "crew motorfest", "motorfest", "wukong",
        "battlefield", "tsushima", "yotei", "assassin", "content warning",
        "rooftops and alleys", "rooftops", "alleys"
    ]):
        game = "Other Games"

    # Timeline-Anchored Fallbacks
    elif "2024-06-05" <= d <= "2024-10-06":
        game = "Helldivers 2"
    elif "2024-10-07" <= d <= "2024-10-21":
        game = "Dragon Ball: Sparking! ZERO"
    elif "2024-10-22" <= d <= "2024-11-12":
        game = "Helldivers 2"
    elif "2024-11-13" <= d <= "2025-03-02":
        game = "Call of Duty / Hiatus"
    elif "2025-03-03" <= d <= "2025-09-08":
        game = "Helldivers 2"
    elif "2025-09-09" <= d <= "2025-10-10":
        game = "Skate"
    elif d >= "2025-10-11":
        if "rapmorelikecap" in sound or likes >= 100000:
            game = "Skate"
        elif "linkin park" in sound or "belong" in sound or likes >= 40000:
            game = "Skate"
        elif "tmnt" in sound or "turtles" in sound:
            game = "Gaming Mashup"
        else:
            game = "Helldivers 2"
    else:
        game = "Other Games"

    # =========================================================================
    # 2. SUB-THEME / CREATIVE INTENT
    # =========================================================================

    if "2024-06-05" <= d <= "2024-06-11" and game == "Helldivers 2":
        sub_theme = "War Photography (No-HUD Stills)"
    elif "2024-10-07" <= d <= "2024-10-21" and game == "Dragon Ball: Sparking! ZERO":
        sub_theme = "Creator On-Camera / Hype"
    elif game == "Skate":
        if any(k in text for k in ["parkour", "mirror", "rapmorelikecap"]) or likes >= 30000:
            sub_theme = "Mirror's Edge Parkour Series"
        else:
            sub_theme = "Street & Park Skate Lines"
    elif game == "Helldivers 2":
        if any(k in sound for k in ["corpse after corpse", "kanye", "never see me again", "phonk"]):
            sub_theme = "Cinematic / High-Energy Edit"
        elif any(k in sound for k in ["original sound", "gameplay"]):
            sub_theme = "Raw Survival / Intense Fights"
        else:
            sub_theme = "Comedy / Tactical Squad Highlights"
    elif game == "Ready or Not":
        sub_theme = "Tactical Breach & CQB"
    elif game == "Hell Let Loose":
        sub_theme = "Hardcore Mil-Sim Frontline"
    elif game == "Dragon Ball: Sparking! ZERO":
        sub_theme = "Arena Combat & Speculation"
    elif game == "Gaming Mashup":
        sub_theme = "Fast-Paced Cross-Game Montage"
    elif game == "Dying Light: The Beast":
        sub_theme = "Survival & Combat Action"
    else:
        sub_theme = "Gameplay Showcase"

    # =========================================================================
    # 3. CONTENT FORMAT
    # =========================================================================

    if sub_theme == "War Photography (No-HUD Stills)":
        content_format = "Stills / Lightroom War Photos"
    elif sub_theme == "Creator On-Camera / Hype":
        content_format = "Talking Head / Reaction"
    elif any(k in sound for k in ["phonk", "sped up", "theme song", "rapmorelikecap", "linkin park", "kanye", "tmnt"]) or likes >= 5000:
        content_format = "Stylized Edit / Montage"
    else:
        content_format = "Raw Gameplay / Squad Clip"

    return pd.Series(
        [game, sub_theme, content_format],
        index=["Primary_Game", "Sub_Theme", "Content_Format"]
    )

def load_and_clean_tiktok_data(file_path="data.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    video_list = raw_data.get("Post", {}).get("Posts", {}).get("VideoList", [])
    if not video_list:
        raise ValueError("No video records found under Post -> Posts -> VideoList.")

    df = pd.DataFrame(video_list)

    # Clean numeric metrics
    df["Likes"] = pd.to_numeric(df.get("Likes", 0), errors="coerce").fillna(0).astype(int)
    if "NumberOfCollections" in df.columns:
        df["Saves"] = pd.to_numeric(df["NumberOfCollections"], errors="coerce").fillna(0).astype(int)
    else:
        df["Saves"] = 0

    # Parse timestamps
    df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")
    df["Post_Hour"] = df["Date"].dt.hour
    df["Day_Name"] = df["Date"].dt.day_name()
    df["Year_Month"] = df["Date"].dt.to_period("M").astype(str)

    # Clean text columns
    for col in ["Title", "Sound", "AlternateText"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
        else:
            df[col] = ""

    # Multi-dimensional classification
    multi_dim = df.apply(classify_content_multidim, axis=1)
    df["Primary_Game"] = multi_dim["Primary_Game"]
    df["Sub_Theme"] = multi_dim["Sub_Theme"]
    df["Content_Format"] = multi_dim["Content_Format"]
    
    # Composite category for backward compatibility with app.py
    df["Content_Category"] = df["Primary_Game"] + " - " + df["Sub_Theme"]

    # Core performance ratios
    df["Save_Rate_Pct"] = np.where(
        df["Likes"] > 0,
        (df["Saves"] / df["Likes"]) * 100,
        0.0
    ).round(2)

    return df

if __name__ == "__main__":
    df = load_and_clean_tiktok_data("data.json")

    print("\n=======================================================")
    print(f" TOTAL ARCHIVE: {len(df)} POSTS PROCESSED")
    print("=======================================================")

    print("\n--- PERFORMANCE BY PRIMARY GAME ---")
    game_summary = df.groupby("Primary_Game").agg(
        Total_Posts=("Likes", "count"),
        Total_Likes=("Likes", "sum"),
        Avg_Likes=("Likes", "mean"),
        Max_Likes=("Likes", "max")
    ).sort_values(by="Total_Likes", ascending=False)
    game_summary["Avg_Likes"] = game_summary["Avg_Likes"].round(1)
    print(game_summary.to_string())

    print("\n--- PERFORMANCE BY CONTENT FORMAT ---")
    format_summary = df.groupby("Content_Format").agg(
        Total_Posts=("Likes", "count"),
        Total_Likes=("Likes", "sum"),
        Avg_Likes=("Likes", "mean")
    ).sort_values(by="Total_Likes", ascending=False)
    format_summary["Avg_Likes"] = format_summary["Avg_Likes"].round(1)
    print(format_summary.to_string())

    print("\n--- TOP SUB-THEMES (TOP 8 BY LIKES) ---")
    theme_summary = df.groupby(["Primary_Game", "Sub_Theme"]).agg(
        Total_Posts=("Likes", "count"),
        Total_Likes=("Likes", "sum"),
        Avg_Likes=("Likes", "mean")
    ).sort_values(by="Total_Likes", ascending=False).head(8)
    theme_summary["Avg_Likes"] = theme_summary["Avg_Likes"].round(1)
    print(theme_summary.to_string())

    print("\n--- ALL-TIME TOP 5 OUTLIERS ---")
    top_cols = ["Date", "Primary_Game", "Sub_Theme", "Content_Format", "Likes", "Sound"]
    print(df.sort_values(by="Likes", ascending=False)[top_cols].head(5).to_string(index=False))