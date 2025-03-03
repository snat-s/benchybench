import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# Directory containing the JSONL files
directory = 'minesweeper_games'

# Initialize a dictionary to track counts
counts = defaultdict(lambda: {'won': 0, 'lost': 0, 'error': 0, 'timeout': 0})
response_length = defaultdict(list)

# Process each JSONL file
for filename in os.listdir(directory):
    if filename.endswith('.jsonl'):
        filepath = os.path.join(directory, filename)
        model = None
        has_game_end = False
        turn_count = 0
        game_won = False
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get('type') == 'game_start':
                        model = data.get('model')
                    elif data.get('type') == 'move':
                        turn_count += 1
                        explanation_length = len(data.get('explanation', 0))
                        if model:
                            response_length[model].append(explanation_length)
                    elif data.get('type') == 'game_end':
                        has_game_end = True
                        game_won = data.get('game_won', False)
                except json.JSONDecodeError:
                    pass

        if model:
            if has_game_end:
                outcome = 'won' if game_won else 'lost'
            else:
                outcome = 'timeout' if turn_count >= 50 else 'error'
            counts[model][outcome] += 1

print("\nAverage response length per model:")
for model in response_length:
    lengths = response_length[model]
    if lengths:
        avg = sum(lengths) / len(lengths)
        print(f"{model}: {avg:.2f} characters")
    else:
        print(f"{model}: No responses recorded")


# Prepare data for stacked bars
models = list(counts.keys())
print(counts)
categories = ['lost', 'won', 'error', 'timeout']
colors = ['#ff6961', '#77dd77', '#ffb347', '#a9a9a9']  # Red, Green, Orange, Grey

# Create stacked bars
fig, ax = plt.subplots(figsize=(10, 6))
bottom = np.zeros(len(models))

for i, category in enumerate(categories):
    values = [counts[model][category] for model in models]
    ax.bar(models, values, bottom=bottom, label=category, color=colors[i])
    bottom += values

# Customize plot
ax.set_title('Minesweeper Game Outcomes by Model for 10x10 board with 10 bombs', pad=20)
ax.set_ylabel('Number of Games')
ax.set_xlabel('')
ax.legend(title='Outcomes', bbox_to_anchor=(1, 1), loc='upper left')

# Rotate model names 90 degrees
plt.xticks(rotation=90, ha='center', fontsize=9)
plt.tight_layout()

#plt.show()
plt.savefig("wins.png")
