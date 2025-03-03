import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Create the eda directory if it doesn't exist
eda_dir = 'eda'
Path(eda_dir).mkdir(parents=True, exist_ok=True)

# List to collect all move data
data_entries = []

# Directory containing the JSONL files
games_dir = 'minesweeper_games'

# Process each JSONL file in the directory
for filename in os.listdir(games_dir):
    if filename.endswith('.jsonl'):
        filepath = os.path.join(games_dir, filename)
        with open(filepath, 'r') as file:
            model = None
            board_size = 10  # default to 10 if not specified
            for line in file:
                try:
                    entry = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue  # skip invalid lines
                if entry.get('type') == 'game_start':
                    # Update model and board_size for subsequent moves
                    model = entry.get('model')
                    board_size = entry.get('board_size', 10)
                elif entry.get('type') == 'move':
                    if model is not None:
                        move = entry.get('move', {})
                        if not move.get('is_flag', False):
                            x = move.get('x')
                            y = move.get('y')
                            # Check if coordinates are within the board's bounds
                            if x is not None and y is not None:
                                if 0 <= x < board_size and 0 <= y < board_size:
                                    data_entries.append({
                                        'x': x,
                                        'y': y,
                                        'model': model
                                    })

# Create DataFrame from collected data
df = pd.DataFrame(data_entries)

# Check if there's data to plot
if df.empty:
    print("No data available to generate heatmaps.")
else:
    # Generate All-Models Heatmap
    counts_all = df.groupby(['x', 'y']).size().reset_index(name='counts')
    pivot_all = counts_all.pivot(index='y', columns='x', values='counts').fillna(0)
    # Ensure full 10x10 grid
    pivot_all = pivot_all.reindex(index=range(10), columns=range(10), fill_value=0)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_all, annot=False, fmt='g', cmap='viridis', cbar=True)
    plt.title('All Models Heatmap')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.gca().invert_yaxis()  # Invert y-axis to match Minesweeper board layout
    plt.savefig(os.path.join(eda_dir, 'all_models_heatmap.png'))
    plt.close()
    
    # Generate Per-Model Heatmaps
    models = df['model'].unique()
    for model in models:
        model_df = df[df['model'] == model]
        counts_model = model_df.groupby(['x', 'y']).size().reset_index(name='counts')
        pivot_model = counts_model.pivot(index='y', columns='x', values='counts').fillna(0)
        pivot_model = pivot_model.reindex(index=range(10), columns=range(10), fill_value=0)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot_model, annot=False, fmt='g', cmap='viridis', cbar=True)
        plt.title(f'Heatmap for {model}')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.gca().invert_yaxis()
        
        # Sanitize model name for filename
        safe_name = model.replace('/', '_').replace(' ', '_')
        plt.savefig(os.path.join(eda_dir, f'{safe_name}_heatmap.png'))
        plt.close()
