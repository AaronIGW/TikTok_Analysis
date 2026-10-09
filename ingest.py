import json
import pandas as pd
import numpy as np

def classify_content(row):
    # 1. First priority: Check any text that survived in Title, Alt, or Sound
    text = f"{row.get('Title', '')} {row.get('AlternateText', '')} {row.get('Sound', '')}".lower()
    
    if any(k in text for k in ["sparking zero", "dragon ball", "budokai"]):
        return "Dragon Ball: Sparking! ZERO"
    if any(k in text for k in ["helldiver", "super earth", "automaton", "terminid"]):
        return "Helldivers 2"
    if any(k in text for k in ["mirrors edge", "mirror's edge", "parkour"]):
        return "Skate (Mirror's Edge Series)"
    if "cyberpunk" in text or "2077" in text or "killmonger" in text:
        return "Cyberpunk 2077"
    if "ready or not" in text:
        return "Ready or Not"
    if "dying light" in text:
        return "Dying Light: The Beast"
    if "rooftops" in text or "alleys" in text:
        return "Rooftops & Alleys"
    if "yotei" in text or "tsushima" in text:
        return "Ghost of Tsushima / Yōtei"
    if "gta" in text or "los santos" in text:
        return "GTA"

    # 2. Second priority: Fallback to exact timeline windows
    post_date = row.get("Date")
    if pd.isna(post_date):
        return "Unknown / Unclassified"

    # Convert to pure string date format YYYY-MM-DD for clean comparison
    d = post_date.strftime("%Y-%m-%d")

    # Era 1: Initial Helldivers Launch & Photography (Jun 5, 2024 - Oct 6, 2024)
    if "2024-06-05" <= d <= "2024-10-06":
        return "Helldivers 2 (Launch Era)"
    
    # Era 2: Sparking Zero Viral Surge (Oct 7, 2024 - Oct 21, 2024)
    elif "2024-10-07" <= d <= "2024-10-21":
        return "Dragon Ball: Sparking! ZERO"
    
    # Era 3: Fall Helldivers Return (Oct 22, 2024 - Nov 12, 2024)
    elif "2024-10-22" <= d <= "2024-11-12":
        return "Helldivers 2 (Fall Return)"
    
    # Gap / Single post (Nov 13, 2024 - Mar 2, 2025)
    elif "2024-11-13" <= d <= "2025-03-02":
        return "Call of Duty / Hiatus"

    # Era 4: Spring/Summer Prime - Heavy Helldivers & Early Tactical (Mar 3, 2025 - Sep 16, 2025)
    elif "2025-03-03" <= d <= "2025-09-16":
        return "Helldivers 2 (Core Stride)"

    # Era 5: The Viral Skate / Mirror's Edge Launch (Sep 17, 2025 - Oct 5, 2025)
    elif "2025-09-17" <= d <= "2025-10-05":
        return "Skate (Mirror's Edge Series)"

    # Era 6: Mashup Variety & Experimentation (Oct 6, 2025 - Jan 22, 2026)
    elif "2025-10-06" <= d <= "2026-01-22":
        return "Gaming Mashup (Helldivers/Skate/Dying Light)"

    # Era 7: Modern Variety & Lifestyle Gaming (Feb 21, 2026 - Present)
    elif d >= "2026-01-23":
        return "Current Variety (Helldivers/Skate/GTA/Friends)"

    return "Other / Miscellaneous"

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

    # Classify content
    df["Content_Category"] = df.apply(classify_content, axis=1)

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

    print("\n--- PERFORMANCE BY ERA / CATEGORY ---")
    era_summary = df.groupby("Content_Category").agg(
        Total_Posts=("Likes", "count"),
        Total_Likes=("Likes", "sum"),
        Avg_Likes=("Likes", "mean"),
        Max_Likes=("Likes", "max")
    ).sort_values(by="Total_Likes", ascending=False)
    
    era_summary["Avg_Likes"] = era_summary["Avg_Likes"].round(1)
    print(era_summary.to_string())

    print("\n--- ALL-TIME TOP 5 OUTLIERS ---")
    top_cols = ["Date", "Content_Category", "Likes", "Saves", "Sound"]
    print(df.sort_values(by="Likes", ascending=False)[top_cols].head(5).to_string(index=False))