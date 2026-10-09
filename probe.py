import json
import pandas as pd

with open("data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

videos = raw_data.get("Post", {}).get("Posts", {}).get("VideoList", [])
df = pd.DataFrame(videos)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Likes"] = pd.to_numeric(df["Likes"], errors="coerce").fillna(0).astype(int)
df = df.sort_values(by="Date", ascending=True)

print("--- POSTING TIMELINE ---")
print(f"Earliest Post: {df['Date'].min()}")
print(f"Latest Post:   {df['Date'].max()}")

print("\n--- POST VOLUME BY MONTH ---")
print(df["Date"].dt.to_period("M").value_counts().sort_index())

print("\n--- TOP 10 MOST FREQUENT SOUNDS ---")
print(df["Sound"].value_counts().head(10))