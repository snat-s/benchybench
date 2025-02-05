#!/usr/bin/env python3
import os
import json
import glob
from datetime import datetime
import argparse
import math

# Elo parameters
K = 32
INITIAL_RATING = 1500

# Define a ranking for game result strings.
RESULT_RANK = {"won": 2, "tie": 1, "lost": 0}

def get_pair_result(result_i, result_j):
    """
    Given the result strings (e.g., "won", "lost", "tie") for two players,
    return a tuple (S_i, S_j) representing the head-to-head score:
      - S = 1 means win, 0 means loss, 0.5 means tie.
    If both players have the same result (e.g., both "won"), treat it as a tie.
    """
    rank_i = RESULT_RANK.get(result_i, 1)
    rank_j = RESULT_RANK.get(result_j, 1)
    if rank_i > rank_j:
        return 1, 0
    elif rank_i < rank_j:
        return 0, 1
    else:
        return 0.5, 0.5

def expected_score(rating_i, rating_j):
    """Compute the expected score for player i vs. player j."""
    return 1 / (1 + 10 ** ((rating_j - rating_i) / 400))

def process_game(game_data, ratings):
    """
    Process one game and update the 'ratings' dictionary (for Elo).
    Returns updated ratings.
    """
    metadata = game_data.get("metadata", {})
    models = metadata.get("models", {})          # {player_id: model_name}
    game_result = metadata.get("game_result", {})  # {player_id: "won"/"lost"/"tie"}
    player_ids = list(models.keys())
    n = len(player_ids)
    
    # Ensure all models exist in our ratings dictionary
    for pid in player_ids:
        model = models[pid]
        if model not in ratings:
            ratings[model] = INITIAL_RATING

    # For each model (player) in this game, accumulate actual/expected scores
    score_sum = { models[pid]: 0 for pid in player_ids }
    expected_sum = { models[pid]: 0 for pid in player_ids }
    
    # Loop over all unordered pairs of players
    for i in range(n):
        for j in range(i+1, n):
            pid_i = player_ids[i]
            pid_j = player_ids[j]
            model_i = models[pid_i]
            model_j = models[pid_j]
            res_i = game_result.get(pid_i, "tie")
            res_j = game_result.get(pid_j, "tie")
            
            # Determine the head-to-head result
            S_i, S_j = get_pair_result(res_i, res_j)
            
            # Compute expected scores from the current ratings
            R_i = ratings[model_i]
            R_j = ratings[model_j]
            E_i = expected_score(R_i, R_j)
            E_j = expected_score(R_j, R_i)
            
            # Accumulate results
            score_sum[model_i] += S_i
            score_sum[model_j] += S_j
            expected_sum[model_i] += E_i
            expected_sum[model_j] += E_j

    # Update each player's rating
    for pid in player_ids:
        model = models[pid]
        delta = (K / (n - 1)) * (score_sum[model] - expected_sum[model]) if (n > 1) else 0
        ratings[model] += delta

    return ratings

### ADDED FOR STATS ###
def update_model_stats(game_data, stats, ratings):
    """
    Updates stats for each model after one game:
      - Increments wins/losses/ties
      - Adds to total apples eaten
      - Syncs the Elo rating from 'ratings'
      - Appends a game history record with details including:
          game_id, my_score, opponent_score, opponent_model, result,
          and, if applicable, death_info.
    """
    metadata = game_data.get("metadata", {})
    game_id = metadata.get("game_id")
    models = metadata.get("models", {})          # {player_id: model_name}
    game_result = metadata.get("game_result", {})  # {player_id: "won"/"lost"/"tie"}
    final_scores = metadata.get("final_scores", {}) # {player_id: score}
    death_info = metadata.get("death_info", {})    # {player_id: death info dictionary}
    
    # For each player in the game...
    for pid, model_name in models.items():
        # Ensure this model is in stats
        if model_name not in stats:
            stats[model_name] = {
                "wins": 0,
                "losses": 0,
                "ties": 0,
                "apples_eaten": 0,
                "elo": INITIAL_RATING,
                "games": []  # New field for game history tracking
            }
        
        # Update W/L/T counts
        result = game_result.get(pid, "tie")
        if result == "won":
            stats[model_name]["wins"] += 1
        elif result == "lost":
            stats[model_name]["losses"] += 1
        else:
            stats[model_name]["ties"] += 1
        
        # Update apples eaten
        apples = final_scores.get(pid, 0)
        stats[model_name]["apples_eaten"] += apples
        
        # Update current Elo rating
        stats[model_name]["elo"] = ratings[model_name]
        
        # Determine opponent's score and opponent's model.
        if len(models) == 2:
            opponent_pid = [other for other in models if other != pid][0]
            opponent_score = final_scores.get(opponent_pid, 0)
            opponent_model = models.get(opponent_pid)
        else:
            opponent_score = None
            opponent_model = None
        
        # Build game history record for this model
        game_record = {
            "game_id": game_id,
            "my_score": final_scores.get(pid, 0),
            "opponent_score": opponent_score,
            "opponent_model": opponent_model,
            "result": result,
            "start_time": metadata.get("start_time"),
            "end_time": metadata.get("end_time")
        }
        
        # Include death_info if this model died in this game.
        if pid in death_info:
            game_record["death_info"] = death_info[pid]
        
        # Append the record to the model's game history list.
        stats[model_name]["games"].append(game_record)

def summarize_game_results(models, game_result):
    """
    Summarizes both the overall game result and the pairwise matchups.
    Returns a tuple of strings for (overall_summary, matchup_summary)
    """
    # Sort by rank (won>tie>lost) just for display
    results = []
    for pid, model in models.items():
        result = game_result.get(pid, "tie")
        rank = RESULT_RANK.get(result, 1)
        results.append((rank, result, model))
    
    results.sort(reverse=True)
    overall = "Overall result:\n"
    for _, result, model in results:
        overall += f"  {model}: {result}\n"
    
    # Pairwise
    matchups = "Pairwise matchups:\n"
    player_ids = list(models.keys())
    for i in range(len(player_ids)):
        for j in range(i+1, len(player_ids)):
            pid_i = player_ids[i]
            pid_j = player_ids[j]
            model_i = models[pid_i]
            model_j = models[pid_j]
            res_i = game_result.get(pid_i, "tie")
            res_j = game_result.get(pid_j, "tie")
            score_i, score_j = get_pair_result(res_i, res_j)
            if score_i == 0.5:
                result_str = "ties"
            elif score_i == 1:
                result_str = "wins against"
            else:
                result_str = "loses to"
            matchups += f"  {model_i} {result_str} {model_j}\n"
    
    return overall, matchups

def main():
    parser = argparse.ArgumentParser(
        description="Calculate Elo ratings and gather stats from a folder of game result JSON files."
    )
    parser.add_argument("folder", help="Path to folder containing game result JSON files.")
    parser.add_argument("--output", help="Path to output folder for stats.json")
    args = parser.parse_args()

    # Find all JSON files
    files = glob.glob(os.path.join(args.folder, "*.json"))
    games = []

    for filename in files:
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                # We sort by end_time so we process in chronological order
                end_time_str = data.get("metadata", {}).get("end_time")
                if end_time_str:
                    end_time = datetime.fromisoformat(end_time_str)
                else:
                    end_time = datetime.min
                games.append((end_time, data))
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # Sort the games by their end_time
    games.sort(key=lambda tup: tup[0])

    # Elo ratings dict: model -> rating
    ratings = {}
    # Stats dict: model -> {"wins", "losses", "ties", "apples_eaten", "elo"}
    stats = {}

    print("Initial Elo ratings:")
    print(f"  (New models start at {INITIAL_RATING})")
    print("-" * 40)
    print("\nProcessing games in chronological order...\n")

    for end_time, game_data in games:
        metadata = game_data.get("metadata", {})
        models = metadata.get("models", {})
        game_result = metadata.get("game_result", {})

        print(f"\nGame finished at {end_time.isoformat()}:")
        overall_summary, matchup_summary = summarize_game_results(models, game_result)
        print(overall_summary)
        print(matchup_summary)
        
        # Update ratings
        ratings = process_game(game_data, ratings)

        # Update stats (wins, losses, ties, apples, Elo)
        update_model_stats(game_data, stats, ratings)

        print("Updated Elo ratings:")
        for model, rating in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: {rating:.2f}")
        print("-" * 40)

    ### ADDED FOR STATS: SAVE stats.json ###
    # Write out stats aggregated across all games
    output_path = os.path.join(args.output, "stats.json")
    with open(output_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nAggregated stats saved to {output_path}")

if __name__ == "__main__":
    main()
