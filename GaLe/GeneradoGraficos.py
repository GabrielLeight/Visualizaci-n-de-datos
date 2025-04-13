import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import json

# Load the JSON lines file
file_path = "../hltb.jsonlines"
with open(file_path, "r", encoding="utf-8") as file:
    data = [json.loads(line) for line in file]

df = pd.DataFrame(data)
# Filter only Xbox 360 games
df = df[df["Stats"].apply(lambda s: "Platform" in s and "Xbox 360" in s["Platform"])]


# Genre mapping
genre_map = {
    "Action": ["Action", "Hack and Slash", "Beat 'em Up", "Combat"],
    "Adventure": ["Adventure", "Point and Click"],
    "Shooter": ["Shooter", "First-Person", "Third-Person", "Top-Down Shooter", "Rail Shooter"],
    "RPG": ["Role-Playing", "JRPG", "Action RPG", "Card Game", "Tactical RPG"],
    "Platformer": ["Platform", "Side-Scrolling", "2D", "3D Platformer"],
    "Racing": ["Racing", "Driving", "Vehicular Combat"],
    "Strategy": ["Strategy", "Tactical", "Turn-Based", "Real-Time", "Tower Defense", "Card Battle"],
    "Sports": ["Sports", "Baseball", "Soccer"],
    "Simulation": ["Simulation", "Life Sim", "Management", "City-Building", "Economy", "Farming"],
    "Puzzle": ["Puzzle", "Logic", "Board Game"],
    "Fighting": ["Fighting", "Arena"],
    "Survival": ["Survival"],
    "Stealth": ["Stealth"],
    "Open World": ["Open World", "Sandbox"],
    "Horror": ["Horror", "Survival Horror"]
}

# Create reverse mapping
reverse_genre_map = {}
for broad, specifics in genre_map.items():
    for specific in specifics:
        reverse_genre_map[specific.lower()] = broad

# Collect games by broad genre
genre_games = defaultdict(list)

for _, row in df.iterrows():
    raw_genres = row.get("Genres")
    name = row.get("Name")
    if not raw_genres or not name:
        continue
    genres = [g.strip().lower() for g in raw_genres.split(",")]
    for g in genres:
        mapped = reverse_genre_map.get(g)
        if mapped:
            genre_games[mapped].append(name)

# Function to convert "23h 17m" → 23.283
def time_to_float(t):
    try:
        if not isinstance(t, str): return 0
        parts = t.lower().replace("hours", "h").replace("hour", "h").replace("minutes", "m").replace("mins", "m").split()
        hours = 0
        minutes = 0
        for part in parts:
            if "h" in part:
                hours += float(part.replace("h", ""))
            elif "m" in part:
                minutes += float(part.replace("m", ""))
        return round(hours + minutes / 60, 2)
    except:
        return 0

# Compute average playtime per genre
genre_playtimes = {}
for genre, games in genre_games.items():
    total_time = 0
    count = 0
    for name in games:
        rows = df[df["Name"] == name]
        for _, r in rows.iterrows():
            stats = r.get("Stats", {})
            main_time = stats.get("Single-Player", {}).get("Main Story", {}).get("Average")
            time = time_to_float(main_time)
            if time > 0:
                total_time += time
                count += 1
    if count > 0:
        genre_playtimes[genre] = round(total_time / count, 2)




        
print(f"Total Xbox 360 games: {len(df)}")
print(f"Genres found: {genre_playtimes}")

# Nightingale (Coxcomb) chart
labels = sorted(genre_playtimes.keys())
values = [genre_playtimes[label] for label in labels]
num_vars = len(values)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

# Duplicate values to close the circle
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))

bars = ax.bar(
    angles,
    values,
    width=2 * np.pi / num_vars,
    bottom=0,
    linewidth=1,
    edgecolor="black",
    color=plt.cm.viridis(np.linspace(0, 1, num_vars)),
    alpha=0.9
)

# Add labels to each wedge
ax.set_xticks(angles)
ax.set_xticklabels(labels, fontsize=11)

# Remove radial labels and customize appearance
ax.set_yticklabels([])
ax.set_title("Average Main Story Playtime by Genre (Xbox 360)", fontsize=16, pad=20)

# Optional: Add value labels on top of bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    angle = bar.get_x() + bar.get_width() / 2
    ax.text(
        angle,
        height + 0.5,
        f"{value:.1f}",
        ha='center',
        va='center',
        fontsize=9,
        rotation=np.degrees(angle),
        rotation_mode='anchor'
    )

plt.tight_layout()
plt.show()
