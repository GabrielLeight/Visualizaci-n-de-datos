import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import json
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import random
# Load the JSON lines file
file_path = "hltb.jsonlines"
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

# Collect data for visualization
genre_data_for_custom = {}
for broad_genre in genre_map:
    genre_games_list = []
    for _, row in df.iterrows():
        raw_genres = row.get("Genres", "")
        name = row.get("Name", "")
        if not raw_genres or not name:
            continue
        genres = [g.strip().lower() for g in raw_genres.split(",")]
        for g in genres:
            mapped_genre = reverse_genre_map.get(g)
            if mapped_genre == broad_genre:
                stats = row.get("Stats", {})
                single_player_stats = stats.get("Single-Player", {})
                main_time_str = single_player_stats.get("Main Story", {}).get("Average", "0h")
                main_time = time_to_float(main_time_str)

                total_dlc_main_time = 0
                dlc_count = 0
                additional_content = stats.get("Additional Content", {})
                for dlc_info in additional_content.values():
                    dlc_main_time_str = dlc_info.get("Main", "0h")
                    total_dlc_main_time += time_to_float(dlc_main_time_str)
                    dlc_count += 1

                avg_dlc_main_time = total_dlc_main_time / dlc_count if dlc_count > 0 else 0

                genre_games_list.append({
                    "name": name,
                    "main_playtime": main_time,
                    "avg_dlc_main_playtime": avg_dlc_main_time,
                    "total_dlc_main_playtime": total_dlc_main_time  # new field for total
                })
    if genre_games_list:
        # Average-based info (keep this)
        total_genre_playtime = sum(game["main_playtime"] for game in genre_games_list)
        avg_genre_playtime = total_genre_playtime / len(genre_games_list)

        total_dlc_playtime_for_genre = sum(game["avg_dlc_main_playtime"] for game in genre_games_list)
        avg_dlc_playtime_for_genre = total_dlc_playtime_for_genre / len(genre_games_list) if len(genre_games_list) > 0 else 0

        comparison_ratio = avg_dlc_playtime_for_genre / avg_genre_playtime if avg_genre_playtime > 0 else 0

        # Total-based info (for background color + font size graph)
        total_main_time = sum(game["main_playtime"] for game in genre_games_list)
        total_dlc_time = sum(game["total_dlc_main_playtime"] for game in genre_games_list)
        total_playtime = total_main_time + total_dlc_time

        genre_data_for_custom[broad_genre] = {
            # Averages (keep)
            "avg_playtime": avg_genre_playtime,
            "dlc_comparison": comparison_ratio,

            # Totals (new)
            "total_main_time": total_main_time,
            "total_dlc_time": total_dlc_time,
            "total_playtime": total_playtime
        }

# --- Config ---
main_color = '#00bfff'
dlc_color = '#ff1744'
text_color = 'white'
bg_color = '#f5f5f5'
font = 'DejaVu Sans'
# --- Sorting and Setup ---# --- Sorting and Setup ---
sorted_genres = sorted(
    genre_data_for_custom.items(),
    key=lambda x: x[1]['total_main_time'] + x[1]['total_dlc_time'],
    reverse=True
)

num_genres = len(sorted_genres)
fig, ax = plt.subplots(figsize=(14, 8))
ax.set_facecolor("#111")
fig.patch.set_facecolor("#111")
ax.axis('off')

# --- Style constants ---
max_total = max(data['total_main_time'] + data['total_dlc_time'] for _, data in sorted_genres)
bar_height = 0.9  # Increased height for more ink
gap = 0.02
text_offset = 0  # Increased offset for better text placement
number_offset = -0.1
# Set initial positions far away from the center
left_start = 0.01  # Start from the left side
right_start = 0.99  # Start from the right side

# Calculate the "movement" towards the center
left_genres_count = (num_genres + 1) // 2  # Half of the genres (even indices)
right_genres_count = num_genres // 2  # Half of the genres (odd indices)

# Define the step for each side
left_step = (0.5 - left_start) / left_genres_count  # Left half: move towards center
right_step = (right_start - 0.5) / right_genres_count  # Right half: move towards center

# Store the bars and text to ensure bars are plotted first
bars = []
texts = []
number_texts = []
for i, (genre, data) in enumerate(sorted_genres):
    total_playtime = data['total_main_time'] + data['total_dlc_time']
    main_ratio = data['total_main_time'] / max_total
    dlc_ratio = data['total_dlc_time'] / max_total

    # Adjust side logic: even index on the left, odd index on the right
    if i % 2 == 0:  # Even genres (left side)
        bar_x = left_start + (i // 2) * left_step
        side = 1  # Left side
    else:  # Odd genres (right side)
        bar_x = right_start - ((i - 1) // 2) * right_step
        side = -1  # Right side

    # --- Plot main bar ---
    main_length = 0.5 * main_ratio
    main_start = bar_x if side == 1 else bar_x - main_length
    bars.append(ax.barh(y=i, width=main_length * side, height=bar_height,
                        left=main_start, color=main_color, alpha=0.9, zorder=1))

    # --- Plot DLC bar ---
    dlc_length = 0.5 * dlc_ratio
    dlc_start = main_start + (main_length * side)
    bars.append(ax.barh(y=i, width=dlc_length * side, height=bar_height,
                        left=dlc_start, color=dlc_color, alpha=0.7, zorder=1))

    # --- Format Time ---
    hours = int(total_playtime)
    minutes = int((total_playtime - hours) * 60)
    time_text = f"{hours}h {minutes:02d}m"

    # --- Calculate total bar length ---
    total_bar_length = main_length + dlc_length

    # --- Genre label text ---
    text_x = dlc_start + (dlc_length + text_offset) * side if data['total_dlc_time'] > 0 else main_start + (main_length + text_offset) * side
    ha = 'left' if side == -1 else 'right'
    texts.append(ax.text(text_x, i, genre.upper(),
                        ha=ha, va='center',
                        fontsize=18 + 10 * (total_playtime / max_total),
                        fontweight='bold',
                        color='white',
                        fontname='DejaVu Sans',
                        path_effects=[pe.withStroke(linewidth=2, foreground='black')], zorder=2))
        

# --- Center slit line ---
ax.axvline(0.5, color='white', alpha=0.15, linewidth=2, linestyle='--')

# --- Config ---
# --- CONFIG ---
legend_lines = []
for genre, data in reversed(sorted_genres):  # Reverse the list
    main = int(data['total_main_time'])
    dlc = int(data['total_dlc_time'])
    legend_lines.append((genre.upper(), (main, dlc)))

# --- Split into Three Sections ---
# First 5 items - Top Left
top_left = legend_lines[:5]
# Next 3 items - Center Right
center_right = legend_lines[5:11]
# Remaining items - Bottom Right
bottom_right = legend_lines[11:]

# --- Layout Settings ---
line_height = 0.045
top_left_x = -0.1  # Far left, top section
center_right_x = 1.2  # Far right, center section
bottom_right_x = 1.05  # Far right, bottom section
y_start_top_left = 0.90  # Top section starts high
y_start_center_right = 0.6  # Center-right section starts in the middle
y_start_bottom_right = 0.2  # Bottom-right section starts low

# --- Function to draw one column ---
def draw_column(data, start_x, ax, start_y, reverse=False):
    for i, (label, (main, dlc)) in enumerate(data):
        y = start_y - i * line_height if not reverse else start_y + i * line_height
        ax.text(start_x, y, f"{label}:", transform=ax.transAxes,
                fontsize=11, va='center', ha='left',
                fontname='DejaVu Sans', color='white',
                path_effects=[pe.withStroke(linewidth=1, foreground='black')],
                bbox=dict(facecolor='none', edgecolor='none', boxstyle="round,pad=0.5"))  # No background box
        ax.text(start_x + 0.18, y, "■", color=main_color, transform=ax.transAxes,
                fontsize=13, va='center', ha='left',
                bbox=dict(facecolor='none', edgecolor='none', boxstyle="round,pad=0.5"))
        ax.text(start_x + 0.21, y, f"{main}h", color='white', transform=ax.transAxes,
                fontsize=11, va='center', ha='left',
                bbox=dict(facecolor='none', edgecolor='none', boxstyle="round,pad=0.5"))
        ax.text(start_x + 0.31, y, "■", color=dlc_color, transform=ax.transAxes,
                fontsize=13, va='center', ha='left',
                bbox=dict(facecolor='none', edgecolor='none', boxstyle="round,pad=0.5"))
        ax.text(start_x + 0.34, y, f"{dlc}h", color='white', transform=ax.transAxes,
                fontsize=11, va='center', ha='left',
                bbox=dict(facecolor='none', edgecolor='none', boxstyle="round,pad=0.5"))

# --- Draw the Three Columns ---
draw_column(top_left, top_left_x, ax, y_start_top_left)  # Top-left reversed for top-down order
draw_column(center_right, center_right_x, ax, y_start_center_right)
draw_column(bottom_right, bottom_right_x, ax, y_start_bottom_right)  # Bottom-right reversed for top-down order

# --- Adjust layout so bars don't change size ---
plt.subplots_adjust(left=0.05, right=0.85, top=0.95, bottom=0.05)  # Modify margins to give space for legend without affecting graph

plt.tight_layout()
plt.show()

# --- Nightingale Chart (as before) ---
labels = sorted(genre_data_for_custom.keys())
values = [genre_data_for_custom[label]["avg_playtime"] for label in labels]
num_vars = len(values)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

# Duplicate values to close the circle
fig_nightingale, ax_nightingale = plt.subplots(figsize=(12, 12), subplot_kw=dict(polar=True))

bars = ax_nightingale.bar(
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
ax_nightingale.set_xticks(angles)
ax_nightingale.set_xticklabels(labels, fontsize=11)

# Remove radial labels and customize appearance
ax_nightingale.set_yticklabels([])
ax_nightingale.set_title("Average Main Story Playtime by Genre (Xbox 360)", fontsize=16, pad=20)

# Optional: Add value labels on top of bars
for bar, value in zip(bars, values):
    height = bar.get_height()
    angle = bar.get_x() + bar.get_width() / 2
    ax_nightingale.text(
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