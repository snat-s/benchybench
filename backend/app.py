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
        print("Getting games")
        # Get the number of games to return from query parameters, default to 10
        limit = request.args.get("limit", default=10, type=int)
        sort_by = request.args.get("sort_by", default="start_time", type=str)

        # Load the game index
        game_index_path = os.path.join(os.getcwd(), "completed_games", "game_index.json")
        with open(game_index_path, "r", encoding="utf-8") as f:
            game_index = json.load(f)

        # Sort the index based on the sort_by parameter
        if sort_by == "start_time":
            sorted_index = sorted(game_index, key=lambda x: x["start_time"], reverse=True)
        elif sort_by == "total_score":
            sorted_index = sorted(game_index, key=lambda x: x["total_score"], reverse=True)
        elif sort_by == "actual_rounds":
            sorted_index = sorted(game_index, key=lambda x: x["actual_rounds"], reverse=True)
        else:
            # For random order, just take random sample directly from index
            selected_games_index = random.sample(game_index, min(limit, len(game_index)))
            sorted_index = None

        # For sorted queries, take only the top N records we need
        if sorted_index is not None:
            selected_games_index = sorted_index[:min(limit, len(sorted_index))]

        # Only load the specific games we need
        valid_games = []
        games_dir = os.path.join(os.getcwd(), "completed_games")
        for record in selected_games_index:
            file_path = os.path.join(games_dir, record["filename"])
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    game_data = json.load(f)
                    valid_games.append(game_data)
            except Exception as e:
                logging.error(f"Error reading or parsing file {file_path}: {e}")
                continue

        print(f"Returning {len(valid_games)} games")
        return jsonify({"games": valid_games})
    
    except Exception as error:
        logging.error(f"Error reading game index or files: {error}")
        return jsonify({"error": "Failed to load game list"}), 500


# Endpoint to mimic the stats API.
# Mimics functionality in frontend/src/app/api/stats/route.ts
@app.route("/api/stats", methods=["GET"])
def get_stats():
    # Get the query parameters: simple for summary stats,
    # model for full stats for a single model
    simple = request.args.get("simple", default=False, type=bool)
    model = request.args.get("model", default=None, type=str)

    if simple:
        # This branch returns the simple version
        stats_path = os.path.join(os.getcwd(), "completed_games", "stats_simple.json")
        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                stats_data = json.load(f)
        except Exception as e:
            logging.error(f"Error loading simple stats data: {e}")
            stats_data = {}
        return jsonify({
            "totalGames": 0,  # You could update this if available in stats_data
            "aggregatedData": stats_data
        })

    # For full stats, we require a model parameter.
    if model is None:
        return jsonify({"error": "Please provide a model parameter for full stats."}), 400

    stats_path = os.path.join(os.getcwd(), "completed_games", "stats.json")
    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            stats_data = json.load(f)
    except Exception as e:
        logging.error(f"Error loading full stats data: {e}")
        return jsonify({"error": "Failed to load stats data."}), 500

    model_stats = stats_data.get(model)
    if model_stats is None:
        return jsonify({"error": f"Stats for model '{model}' not found."}), 404

    # Since the full stats already include wins/losses, simply return the model's stats.
    total_games = model_stats.get("wins", 0) + model_stats.get("losses", 0) + model_stats.get("ties", 0)
    return jsonify({
        "totalGames": total_games,
        "aggregatedData": {model: model_stats}
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