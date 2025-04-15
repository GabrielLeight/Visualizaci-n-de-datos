import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re


def limpiar_tags(tags):
    if pd.isna(tags):
        return []
    
    tags = tags.lower()
    
    reemplazos = {
        r"\b3rd person\b": "third_person",
        r"\bthird-person\b": "third_person",
        r"\bcoop\b": "co_op",
        r"\bcooperative\b": "co_op",
        r"\bco op\b": "co_op",
        r"\bfull controller support\b": "controller_support",
        r"\bpartial controller support\b": "controller_support",
        r"\bsteam cloud\b": "cloud_support",
        r"\bfps\b": "first_person_shooter",
        r"\btps\b": "third_person_shooter",
        r"\bsingleplayer\b": "single_player",
        r"\bmultiplayer\b": "multi_player",
        r"\bonline multi player\b": "multi_player",
        r"\bonline multi-player\b": "multi_player",
        r"\bonline-multi-player\b": "multi_player"
    }

    for original, reemplazo in reemplazos.items():
        tags = re.sub(original, reemplazo, tags)

    # Separar y limpiar
    tag_list = re.split(r"\s*[,\|]\s*", tags.strip())
    
    tags_limpios = []
    for tag in tag_list:
        tag = tag.strip()
        if tag:
            tag = tag.replace(" ", "_")
            tag = tag.replace("-", "_")
            if tag not in tags_limpios:
                tags_limpios.append(tag)
    
    return tags_limpios

df = pd.read_csv("RAWG.io_xbox_games_with_devs.csv")

df['cleaned_tags'] = df['tags'].apply(limpiar_tags)

# Para WordCloud
all_tags = " ".join(" ".join(tags) for tags in df['cleaned_tags'])
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color="white",
    colormap="viridis",
    collocations=False,
    max_words=100,
).generate(all_tags)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("WordCloud de las Tags de Juegos (Xbox)", fontsize=16)
plt.show()



# Violin plot
df["platform_count"] = df["platforms"].apply(lambda x: len(str(x).split(", ")) if pd.notna(x) else 0)

plt.figure(figsize=(8, 6))
sns.violinplot(y=df["platform_count"], inner="quartile", color="royalblue")
plt.title("Distribución de plataformas por juego (Xbox)")
plt.ylabel("Cantidad de plataformas por juego")
plt.grid(True, axis='y', linestyle='--', alpha=0.6)
plt.show()
