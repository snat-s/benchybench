import json
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageSequenceClip
import os
# Replace this with the JSON string you have, or read from file if you prefer

def draw_frame(round_data, metadata, frame_index):
    """
    Draw a single frame showing the board with:
      - Grid
      - Apples
      - Snake positions (in different colors)
      - Labels for snakes by their model names
      - Title showing the round number (and possibly state info)
    Returns a NumPy array (RGB) suitable for making a video frame.
    """
    width = round_data["width"]
    height = round_data["height"]
    snake_positions = round_data["snake_positions"]
    apples = round_data["apples"]
    alive_info = round_data["alive"]
    
    # Model names (for labeling)
    snake1_name = metadata["models"]["1"]
    snake2_name = metadata["models"]["2"]
    
    # Decide on colors: if a snake is dead, color it gray
    snake1_color = 'red' if alive_info.get("1", False) else 'gray'
    snake2_color = 'blue' if alive_info.get("2", False) else 'gray'
    
    # Create a figure
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-0.5, width - 0.5)
    ax.set_ylim(-0.5, height - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(width))
    ax.set_yticks(range(height))
    
    # Plot apples (green circles)
    for (x, y) in apples:
        ax.scatter(x, y, c='green', s=100, marker='o', edgecolors='black')
    
    # Plot snake 1
    if "1" in snake_positions:
        for (x, y) in snake_positions["1"]:
            ax.scatter(x, y, c=snake1_color, s=200, marker='s', edgecolors='black')
        # Label near its head (0th segment)
        if snake_positions["1"]:
            head_x, head_y = snake_positions["1"][0]
            ax.text(head_x + 0.2, head_y, snake1_name, color=snake1_color, fontsize=9, ha='left', va='center')
    
    # Plot snake 2
    if "2" in snake_positions:
        for (x, y) in snake_positions["2"]:
            ax.scatter(x, y, c=snake2_color, s=200, marker='s', edgecolors='black')
        # Label near its head (0th segment)
        if snake_positions["2"]:
            head_x, head_y = snake_positions["2"][0]
            ax.text(head_x + 0.2, head_y, snake2_name, color=snake2_color, fontsize=9, ha='left', va='center')
    
    # Set a title
    round_number = round_data["round_number"]
    ax.set_title(f"Round {round_number} — Frame {frame_index}\nGame ID: {metadata['game_id']}")
    
    # Render the figure, then convert from ARGB to RGB
    fig.canvas.draw()
    dpi = fig.get_dpi()
    width_px = int(fig.get_figwidth() * dpi)
    height_px = int(fig.get_figheight() * dpi)
    
    argb_buffer = fig.canvas.tostring_argb()
    argb_array = np.frombuffer(argb_buffer, dtype='uint8').reshape(height_px, width_px, 4)
    frame_image = argb_array[..., 1:]  # Discards the alpha channel
    
    plt.close(fig)
    return frame_image


def main():
    """
    Main function for looping through all JSON game files in completed_games/.
    Creates a video for each JSON game if it doesn't already exist in videos/.
    The video filename will be the same as the JSON filename with .mp4 extension.
    """
    json_dir = "completed_games"
    video_dir = "videos"

    # Ensure the output directory exists
    os.makedirs(video_dir, exist_ok=True)

    # Loop through every .json file in the completed_games directory
    for json_file in os.listdir(json_dir):
        if not json_file.endswith(".json"):
            continue

        base_name = os.path.splitext(json_file)[0]
        video_filename = base_name + ".mp4"
        video_path = os.path.join(video_dir, video_filename)

        # Skip if video already exists
        if os.path.exists(video_path):
            print(f"Skipping {video_filename} as it already exists.")
            continue

        json_path = os.path.join(json_dir, json_file)
        print(f"Processing {json_path}...")

        # Load the game JSON data
        with open(json_path, "r") as f:
            game_data = json.load(f)

        metadata = game_data["metadata"]
        rounds = game_data["rounds"]

        frames = []
        for i, round_data in enumerate(rounds):
            frame = draw_frame(round_data, metadata, i)
            frames.append(frame)

        # Create a video at 1 frame per second from these frames
        clip = ImageSequenceClip(frames, fps=1)
        clip.write_videofile(video_path, codec="libx264")
        print(f"Video saved to {video_path}\n")

if __name__ == "__main__":
    main()