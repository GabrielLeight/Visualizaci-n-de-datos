import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify  # <- Asegúrate de tenerlo instalado

# Leer el CSV
df = pd.read_csv("RAWG.io_xbox_games_with_devs.csv")

# Filtrar columnas necesarias
df = df[['esrb_rating', 'rating']].dropna()

# Limitar a ESRB más comunes
esrb_valid = ['Everyone', 'Everyone 10+', 'Teen', 'Mature', 'Adults Only']
df = df[df['esrb_rating'].isin(esrb_valid)]

# -----------------------------------
# Bee Swarm Plot
# -----------------------------------
plt.figure(figsize=(10, 6))
sns.swarmplot(data=df, x='esrb_rating', y='rating', palette='Set2')
plt.title("Bee Swarm: Distribución de Ratings por ESRB")
plt.xlabel("Clasificación ESRB")
plt.ylabel("Rating del Juego")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# -----------------------------------
# Treemap: cantidad de juegos por ESRB
# -----------------------------------
esrb_counts = df['esrb_rating'].value_counts()
labels = [f"{label}\n({count})" for label, count in zip(esrb_counts.index, esrb_counts.values)]

plt.figure(figsize=(10, 6))
squarify.plot(sizes=esrb_counts.values, label=labels, alpha=0.8, color=sns.color_palette('Set3'))
plt.title("Treemap: Cantidad de Juegos por Clasificación ESRB")
plt.axis('off')
plt.tight_layout()
plt.show()
