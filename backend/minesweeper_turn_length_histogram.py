import json
import os
import glob
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set the style for the plots
sns.set(style="whitegrid")

# Directory containing the JSONL files
directory = "minesweeper_games"

# Dictionary to store turns by model
model_turns = defaultdict(list)
model_game_counts = defaultdict(int)
model_games = defaultdict(list)

# Process all JSONL files in the directory
for filepath in glob.glob(os.path.join(directory, "*.jsonl")):
    with open(filepath, 'r') as file:
        current_model = None
        current_game_id = None
        current_game_turns = 0
        
        for line in file:
            try:
                data = json.loads(line.strip())
                
                # Extract model name and game ID from game_start event
                if data.get("type") == "game_start":
                    current_model = data.get("model")
                    current_game_id = data.get("game_id")
                    current_game_turns = 0
                    model_game_counts[current_model] += 1
                
                # Count move events as turns
                if data.get("type") == "move" and current_model and current_game_id:
                    current_game_turns += 1
                
                # When game ends, store the total number of turns
                if data.get("type") == "game_end" and current_model and current_game_id:
                    model_turns[current_model].append(current_game_turns)
                    model_games[current_model].append({
                        "game_id": current_game_id,
                        "turns": current_game_turns
                    })
            except json.JSONDecodeError:
                continue

# Calculate average turn length per model
model_avg_turns = {}
all_turn_counts = []

for model, turns in model_turns.items():
    if turns:
        # Calculate average turns
        avg_turns = sum(turns) / len(turns)
        model_avg_turns[model] = {
            "average_turns": avg_turns,
            "total_games": len(turns),
            "games_played": model_game_counts[model]
        }
        # Store all turn counts with model information for the histogram
        for turn_count in turns:
            all_turn_counts.append({
                "model": model,
                "turns": turn_count
            })

# Convert to DataFrame for easier plotting
df = pd.DataFrame(all_turn_counts)

# Create a figure for the average turns bar chart
plt.figure(figsize=(14, 8))
models = list(model_avg_turns.keys())
avg_turns = [stats["average_turns"] for model, stats in model_avg_turns.items()]

# Sort by average turns
sorted_indices = np.argsort(avg_turns)[::-1]
sorted_models = [models[i] for i in sorted_indices]
sorted_turns = [avg_turns[i] for i in sorted_indices]

# Plot average turns
ax = sns.barplot(x=sorted_models, y=sorted_turns)
ax.set_title("Average Turn Length by Model", fontsize=16)
ax.set_xlabel("Model", fontsize=14)
ax.set_ylabel("Average Turns per Game", fontsize=14)

# Rotate x-axis labels by 90 degrees
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("eda/average_turn_length.png")
plt.close()

# Create histograms for each model
plt.figure(figsize=(16, 10))
ax = sns.histplot(data=df, x="turns", hue="model", element="step", bins=30, kde=True)
ax.set_title("Distribution of Turn Counts by Model", fontsize=16)
ax.set_xlabel("Turns per Game", fontsize=14)
ax.set_ylabel("Frequency", fontsize=14)
plt.tight_layout()
plt.savefig("eda/turn_count_distribution.png")
plt.close()

# Create individual histograms for each model
for model in df['model'].unique():
    plt.figure(figsize=(10, 6))
    model_data = df[df['model'] == model]
    ax = sns.histplot(data=model_data, x="turns", bins=25, kde=True)
    ax.set_title(f"Distribution of Turn Counts for {model}", fontsize=16)
    ax.set_xlabel("Turns per Game", fontsize=14)
    ax.set_ylabel("Frequency", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"eda/turn_count_{model.replace('/', '_')}.png")
    plt.close()

# Create a boxplot to compare distributions
plt.figure(figsize=(14, 8))
ax = sns.boxplot(x="model", y="turns", data=df)
ax.set_title("Turn Count Distribution by Model", fontsize=16)
ax.set_xlabel("Model", fontsize=14)
ax.set_ylabel("Turns per Game", fontsize=14)

# Rotate x-axis labels by 90 degrees
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("eda/turn_count_boxplot.png")
plt.close()

# Print results
print("Average Turn Length by Model:")
print("===================================")
for model, stats in sorted(model_avg_turns.items(), key=lambda x: x[1]["average_turns"], reverse=True):
    print(f"{model}:")
    print(f"  Average turns per game: {stats['average_turns']:.2f}")
    print(f"  Total games with turns: {stats['total_games']}")
    print(f"  Games played: {stats['games_played']}")
    print()

print("Visualization files saved:")
print("- average_turn_length.png")
print("- turn_count_distribution.png")
print("- turn_count_boxplot.png")
print("- Individual model histograms")
