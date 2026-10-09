import json

file_name = "data.json"

with open(file_name, 'r', encoding='utf-8') as f:
    data = json.load(f)

posts_list = data.get("Post", {}).get("Posts", {}).get("VideoList", [])

print("--- SEARCHING FOR THE VIRAL MASTERPIECE ---\n")

for vid in posts_list:
    likes = int(vid.get("Likes", "0"))
    
    # This is the "Sniper" logic: Only show videos with > 100k likes
    if likes > 10000:
        print(f"🎯 FOUND IT!")
        print(f"📅 DATE: {vid.get('Date')}")
        print(f"❤️ LIKES: {likes}")
        print(f"🎵 SOUND: {vid.get('Sound')}")
        print(f"🔗 LINK: {vid.get('Link')}")
        print("-" * 30)

# If nothing prints, try lowering 100000 to 50000 to see the next tier!