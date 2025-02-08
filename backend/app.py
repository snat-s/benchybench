import os
import json
import random
import logging
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Endpoint to mimic GET requests for a list of games.
# Mimics functionality in frontend/src/app/api/games/route.ts
@app.route("/api/games", methods=["GET"])
def get_games():
    try:
        # Get the number of games to return from query parameters, default to 10.
        limit = request.args.get("limit", default=10, type=int)
        sort_by = request.args.get("sort_by", default="start_time", type=str)
        
        # Build the directory path for completed games.
        # This assumes you're running the backend from your project root.
        games_dir = os.path.join(os.getcwd(), "completed_games")
        
        # Attempt to list all files in the directory.
        files = os.listdir(games_dir)
        
        # Filter for snake game files that start with 'snake_game_' and end with '.json'.
        snake_game_files = [
            file for file in files
            if file.startswith("snake_game_") and file.endswith(".json")
        ]
        
        # Randomly shuffle the list and select up to 'limit' game files.
        if sort_by == "start_time":
            # Read all game files to sort by actual start_time from metadata
            game_files_with_time = []
            for file in snake_game_files:
                try:
                    with open(os.path.join(games_dir, file), "r", encoding="utf-8") as f:
                        game_data = json.load(f)
                        start_time = game_data["metadata"]["start_time"]
                        game_files_with_time.append((file, start_time))
                except Exception as e:
                    logging.error(f"Error reading {file}: {e}")
                    continue
            
            # Sort by start_time, most recent first
            game_files_with_time.sort(key=lambda x: x[1], reverse=True)
            snake_game_files = [file for file, _ in game_files_with_time]
        elif sort_by == "actual_rounds":
            # Read all game files to sort by actual_rounds from metadata
            game_files_with_rounds = []
            for file in snake_game_files:
                try:
                    with open(os.path.join(games_dir, file), "r", encoding="utf-8") as f:
                        game_data = json.load(f)
                        rounds = game_data["metadata"]["actual_rounds"]
                        game_files_with_rounds.append((file, rounds))
                except Exception as e:
                    logging.error(f"Error reading {file}: {e}")
                    continue
            
            # Sort by actual_rounds, most rounds first
            game_files_with_rounds.sort(key=lambda x: x[1], reverse=True)
            snake_game_files = [file for file, _ in game_files_with_rounds]
        elif sort_by == "total_score":
            # Read all game files to sort by total score from metadata
            game_files_with_score = []
            for file in snake_game_files:
                try:
                    with open(os.path.join(games_dir, file), "r", encoding="utf-8") as f:
                        game_data = json.load(f)
                        final_scores = game_data["metadata"]["final_scores"]
                        total_score = sum(final_scores.values())
                        game_files_with_score.append((file, total_score))
                except Exception as e:
                    logging.error(f"Error reading {file}: {e}")
                    continue
            
            # Sort by total score, highest first
            game_files_with_score.sort(key=lambda x: x[1], reverse=True)
            snake_game_files = [file for file, _ in game_files_with_score]
        else:
            random.shuffle(snake_game_files)
        
        selected_files = snake_game_files[:min(limit, len(snake_game_files))]
        
        valid_games = []
        for file in selected_files:
            file_path = os.path.join(games_dir, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    game_data = json.load(f)
                    valid_games.append(game_data)
            except Exception as e:
                logging.error(f"Error reading or parsing {file_path}: {e}")
                continue
        
        # Return the game data as JSON.
        return jsonify({"games": valid_games})
    
    except Exception as error:
        logging.error(f"Error reading game directory: {error}")
        return jsonify({"error": "Failed to load game list"}), 500


# Endpoint to mimic the stats API.
# Mimics functionality in frontend/src/app/api/stats/route.ts
@app.route("/api/stats", methods=["GET"])
def get_stats():
    try:
        # Build the path to the stats JSON file.
        stats_path = os.path.join(os.getcwd(), "completed_games", "stats.json")
        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading stats data: {e}")
            stats_data = {}
        
        total_games = 0
        # Iterate through each player's stats entry to aggregate the game counts.
        if isinstance(stats_data, dict):
            for player, entry in stats_data.items():
                wins = entry.get("wins", 0)
                losses = entry.get("losses", 0)
                ties = entry.get("ties", 0)
                total_games += wins + losses + ties
        
        return jsonify({
            "totalGames": total_games,
            "aggregatedData": stats_data or {}
        })
    
    except Exception as error:
        logging.error(f"Error processing stats: {error}")
        return jsonify({
            "totalGames": 0,
            "aggregatedData": {}
        })


# Endpoint to get details for a single game by id.
# Mimics functionality in frontend/src/app/api/games/[gameId]/route.ts
@app.route("/api/matches/<match_id>", methods=["GET"])
def get_game_by_id(match_id):
    try:
        # Construct the file path using the game_id.
        match_filename = f"snake_game_{match_id}.json"
        match_file_path = os.path.join(os.getcwd(), "completed_games", match_filename)

        with open(match_file_path, "r", encoding="utf-8") as f:
            match_data = json.load(f)
        
        return jsonify(match_data)
    
    except Exception as error:
        logging.error(f"Error reading match data for match id {match_id}: {error}")
        return jsonify({"error": "Failed to load match data"}), 500

if __name__ == "__main__":
    # Run the Flask app in debug mode.
    app.run(debug=os.getenv("FLASK_DEBUG"))