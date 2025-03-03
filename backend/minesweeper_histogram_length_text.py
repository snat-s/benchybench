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
plt.figure(figsize=(12, 8))

# Directory containing the JSONL files
directory = "minesweeper_games"

# Dictionary to store explanations by model
model_explanations = defaultdict(list)
model_game_counts = defaultdict(int)

# Process all JSONL files in the directory
for filepath in glob.glob(os.path.join(directory, "*.jsonl")):
    with open(filepath, 'r') as file:
        current_model = None
        
        for line in file:
            try:
                data = json.loads(line.strip())
                
                # Extract model name from game_start event
                if data.get("type") == "game_start":
                    current_model = data.get("model")
                    model_game_counts[current_model] += 1
                
                # Extract explanation from move events
                if data.get("type") == "move" and current_model:
                    # Check if explanation is directly in the move object or at the top level
                    if "explanation" in data:
                        explanation = data["explanation"]
                        model_explanations[current_model].append(explanation)
                    elif "explanation" in data.get("move", {}):
                        explanation = data["move"]["explanation"]
                        model_explanations[current_model].append(explanation)
                
            except json.JSONDecodeError:
                continue

# Calculate average explanation length per model
model_avg_lengths = {}
all_explanation_lengths = []

for model, explanations in model_explanations.items():
    if explanations:
        # Calculate lengths for each explanation
        lengths = [len(explanation) for explanation in explanations]
        
        # Store the average
        avg_length = sum(lengths) / len(lengths)
        model_avg_lengths[model] = {
            "average_length": avg_length,
            "total_explanations": len(explanations),
            "games_played": model_game_counts[model]
        }
        
        # Store all lengths with model information for the histogram
        for length in lengths:
            all_explanation_lengths.append({
                "model": model,
                "length": length
            })

# Convert to DataFrame for easier plotting
df = pd.DataFrame(all_explanation_lengths)

# Create a figure for the average lengths bar chart
plt.figure(figsize=(14, 8))
models = list(model_avg_lengths.keys())
avg_lengths = [stats["average_length"] for model, stats in model_avg_lengths.items()]

# Sort by average length
sorted_indices = np.argsort(avg_lengths)[::-1]
sorted_models = [models[i] for i in sorted_indices]
sorted_lengths = [avg_lengths[i] for i in sorted_indices]

# Plot average lengths
ax = sns.barplot(x=sorted_models, y=sorted_lengths)
ax.set_title("Average Explanation Length by Model", fontsize=16)
ax.set_xlabel("Model", fontsize=14)
ax.set_ylabel("Average Length (characters)", fontsize=14)

# Rotate x-axis labels by 90 degrees
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("eda/average_explanation_length.png")
plt.close()

# Create histograms for each model
plt.figure(figsize=(16, 10))
ax = sns.histplot(data=df, x="length", hue="model", element="step", bins=30, kde=True)
ax.set_title("Distribution of Explanation Lengths by Model", fontsize=16)
ax.set_xlabel("Explanation Length (characters)", fontsize=14)
ax.set_ylabel("Frequency", fontsize=14)
plt.tight_layout()
plt.savefig("eda/explanation_length_distribution.png")
plt.close()

# Create individual histograms for each model
for model in df['model'].unique():
    plt.figure(figsize=(10, 6))
    model_data = df[df['model'] == model]
    ax = sns.histplot(data=model_data, x="length", bins=25, kde=True)
    ax.set_title(f"Distribution of Explanation Lengths for {model}", fontsize=16)
    ax.set_xlabel("Explanation Length (characters)", fontsize=14)
    ax.set_ylabel("Frequency", fontsize=14)
    plt.tight_layout()
    plt.savefig(f"eda/explanation_length_{model.replace('/', '_')}.png")
    plt.close()

# Create a boxplot to compare distributions
plt.figure(figsize=(14, 8))
ax = sns.boxplot(x="model", y="length", data=df)
ax.set_title("Explanation Length Distribution by Model", fontsize=16)
ax.set_xlabel("Model", fontsize=14)
ax.set_ylabel("Explanation Length (characters)", fontsize=14)

# Rotate x-axis labels by 90 degrees
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("eda/explanation_length_boxplot.png")
plt.close()

# Print results
print("Average Explanation Length by Model:")
print("===================================")
for model, stats in sorted(model_avg_lengths.items(), key=lambda x: x[1]["average_length"], reverse=True):
    print(f"{model}:")
    print(f"  Average explanation length: {stats['average_length']:.2f} characters")
    print(f"  Total explanations: {stats['total_explanations']}")
    print(f"  Games played: {stats['games_played']}")
    print()

print("Visualization files saved:")
print("- average_explanation_length.png")
print("- explanation_length_distribution.png")
print("- explanation_length_boxplot.png")
print("- Individual model histograms")
