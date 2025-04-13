import json
import pandas as pd

xbox_360_games = []

with open("../hltb.jsonlines", "r", encoding="utf-8") as file:
    for line in file:
        game = json.loads(line)
        platforms = game.get("Stats", {}).get("Platform", {})
        if "Xbox 360" in platforms:
            playtimes = platforms["Xbox 360"]
            xbox_360_games.append({
                "Name": game["Name"],
                "Genre": game.get("Genres", "Unknown"),
                "Release Date": game.get("Release_date", "Unknown"),
                "Main": playtimes.get("Main", "N/A"),
                "Main +": playtimes.get("Main +", "N/A"),
                "100%": playtimes.get("100%", "N/A")
            })

df = pd.DataFrame(xbox_360_games)
df.to_excel("xbox_360_games_playtimes.xlsx", index=False)
print("✅ Saved to 'xbox_360_games_playtimes.xlsx'")
