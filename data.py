
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("scores/me_at_the_zoo.in/hillclimb.csv")  # Change to your actual path
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df.dropna(subset=['score'], inplace=True)

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='solution_id', y='score', hue='algorithm', marker='o')
plt.title("Algorithm Score Over Time")
plt.xlabel("Solution ID (Time)")
plt.ylabel("Score")
plt.grid(True)
plt.tight_layout()
plt.show()
