import json
import time
from typing import List, Dict
import os

class MinesweeperVisualizer:
    def __init__(self, game_data: List[Dict]):
        self.game_data = game_data
        self.current_step = 0
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def format_board(self, board: str) -> str:
        """Format the board for display"""
        # Remove any existing ANSI codes if present
        lines = board.split('\n')
        # Ensure consistent spacing
        return '\n'.join(f"{line:<30}" for line in lines)
        
    def display_current_state(self):
        """Display the current game state with move information"""
        self.clear_screen()
        current_data = self.game_data[self.current_step]
        
        # Print game info
        if current_data['type'] == 'game_start':
            print(f"Game Start - Board Size: {current_data['board_size']}x{current_data['board_size']}, Bombs: {current_data['bomb_number']}")
            board = current_data['initial_board']
        elif current_data['type'] == 'game_end':
            print(f"Game End - {'Won!' if current_data['game_won'] else 'Lost!'}")
            board = current_data['final_board']
        else:
            print(f"Move {self.current_step} - Flags remaining: {current_data['flags_remaining']}")
            if 'move' in current_data:
                move = current_data['move']
                move_type = 'Flag' if move['is_flag'] else 'Reveal'
                print(f"Action: {move_type} at position ({move['x']}, {move['y']})")
                print(f"Success: {'Yes' if current_data.get('sucess', True) else 'No'}")
            board = current_data['board_state']
            
        # Print the board
        print("\nBoard:")
        print(self.format_board(board))
        
        if 'explanation' in current_data:
            print("\nExplanation:")
            print(current_data['explanation'])
            
        print("\nControls:")
        print("n: Next move")
        print("p: Previous move")
        print("q: Quit")
        print(f"Current step: {self.current_step + 1}/{len(self.game_data)}")
        
    def run(self):
        """Run the visualization with interactive controls"""
        while True:
            self.display_current_state()
            command = input("\nEnter command: ").lower()
            
            if command == 'n' and self.current_step < len(self.game_data) - 1:
                self.current_step += 1
            elif command == 'p' and self.current_step > 0:
                self.current_step -= 1
            elif command == 'q':
                break
            else:
                print("Invalid command!")
                time.sleep(1)

def parse_game_data(text: str) -> List[Dict]:
    """Parse the game data from the text file"""
    return [json.loads(line) for line in text.strip().split('\n')]

def main():
    filename = './completed_games/minesweeper_game_60222745-f814-42ff-b6fb-9d3a0896936e.jsonl'
    try:
        # Read the game data
        with open(filename, 'r') as f:
            game_data = parse_game_data(f.read())
        
        # Create and run the visualizer
        visualizer = MinesweeperVisualizer(game_data)
        visualizer.run()
    except FileNotFoundError:
        print(f"Error: Could not find file '{filename}'")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON data in file '{filename}'")

if __name__ == "__main__":
    main()
