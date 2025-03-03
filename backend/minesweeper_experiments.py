import os
import uuid
import time
from typing import List
from datetime import datetime
from tqdm import tqdm
from minesweeper import MineSweeper, MineSweeperLLMGamer

# List of models to test
MODELS = [
        #"meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        #"meta-llama/Llama-3.3-70B-Instruct-Turbo",
        #"mistralai/Mistral-Small-24B-Instruct-2501",
        #"claude-3-5-sonnet-20241022",
        #"claude-3-5-haiku-20241022",
        #"o3-mini-2025-01-31", <- needs testing
        #"o1-2024-12-17", <- needs testing
        #"gpt-4o-2024-08-06",
        #"gpt-4o-mini-2024-07-18",
        #"deepseek-ai/DeepSeek-V3",
        #"deepseek-ai/DeepSeek-R1",
        #"Qwen/Qwen2.5-72B-Instruct-Turbo", 
        #"Qwen/QwQ-32B-Preview"
        #"deepseek-ai/DeepSeek-V3",
        #"gemini-2.0-flash-lite-preview-02-05",
        #"gemini-2.0-flash-thinking-exp-01-21", # <- errors on their API wtf
        #"claude-3-7-sonnet-20250219"
        #"claude-3-7-sonnet-20250219-thinking",
        #"o1-mini-2024-09-12", 
        #"o1-preview-2024-09-12",
        "deepseek-r1-distill-llama-70b",
        #"deepseek-r1-distill-qwen-32b",
]

RUNS_PER_MODEL = 50
BOARD_SIZE = 10
BOMB_NUMBER = 10

def run_single_game(model: str) -> dict:
    """Run a single game with the specified model and return the results."""
    try:
        #time.sleep(20)
        player = MineSweeperLLMGamer(str(uuid.uuid4()), model=model)
        game = MineSweeper(board_size=BOARD_SIZE, bomb_number=BOMB_NUMBER, model=model)
        
        is_game_playing = True
        turn_count = 0
        max_turns = 50 # i'm sorry but i don't have infinite compute, 50 seems like you could click half the board, seems like non optimal but good enough.

        while is_game_playing and turn_count < max_turns:
            move = None
            while move is None:
                move = player.get_move(game)
                if isinstance(move, str) and move == "retry":
                    move = None
            
            is_game_playing = game.play_move(move)
            turn_count += 1

        # If we hit the turn limit, consider it a loss
        if turn_count >= max_turns:
            game.game_won = False
            is_game_playing = False
            
        return {
            "model": model,
            "game_id": game.game_id,
            "won": game.game_won,
            "moves_file": game.moves_file
        }
    except Exception as e:
        print(f"Error in game with model {model}: {str(e)}")
        return {
            "model": model,
            "error": str(e)
        }

def run_experiments():
    """Run experiments for all models with specified number of runs."""
    # Create directory for game results if it doesn't exist
    os.makedirs("minesweeper_games", exist_ok=True)
    
    # Store results for each model
    results = {model: {"wins": 0, "total": 0, "errors": 0} for model in MODELS}
    
    # Run games sequentially for each model
    for model in tqdm(MODELS, desc="Models", position=0):
        for run in tqdm(range(RUNS_PER_MODEL), desc=f"Games for {model}", position=1, leave=False):
            result = run_single_game(model)
            
            if "error" in result:
                results[model]["errors"] += 1
            else:
                results[model]["total"] += 1
                if result["won"]:
                    results[model]["wins"] += 1
            
            # Update progress bar description with current stats
            wins = results[model]["wins"]
            total = results[model]["total"]
            errors = results[model]["errors"]
            win_rate = (wins / total * 100) if total > 0 else 0
            
            tqdm.write(f"{model} - Win rate: {win_rate:.2f}% ({wins}/{total}), Errors: {errors}")
    
    # Print final results
    print("\nFinal Results:")
    print("=" * 50)
    for model in MODELS:
        wins = results[model]["wins"]
        total = results[model]["total"]
        errors = results[model]["errors"]
        win_rate = (wins / total * 100) if total > 0 else 0
        
        print(f"\nModel: {model}")
        print(f"Wins: {wins}/{total} ({win_rate:.2f}%)")
        print(f"Errors: {errors}")

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Starting experiments at {start_time}")
    
    run_experiments()
    
    end_time = datetime.now()
    print(f"\nExperiments completed at {end_time}")
    print(f"Total duration: {end_time - start_time}")
