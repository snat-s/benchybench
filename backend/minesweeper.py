import random
import uuid
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Literal, Tuple, Optional
from llm_providers import create_llm_provider
from main import Player, GameState

load_dotenv(".env.local")

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]
@dataclass
class Tile:
    is_bomb: bool = False
    is_revealed: bool = False
    is_flagged: bool = False
    adjacent_bombs: int = 0

class Board:
    def __init__(self, board_size=5, number_of_mines=5):
        self.board_size=board_size
        self.number_of_mines=number_of_mines
        self.board: List[List[Tile]] = [[Tile() for _ in range(self.board_size)] for _ in range(self.board_size)]
        self._init_board()

    def _init_board(self):
        """Randomly init the board."""
        all_possible_places = [(i, j) for i in range(self.board_size) for j in range(self.board_size)]
        bombs = random.sample(all_possible_places, self.number_of_mines)
        for x, y in bombs:
            self.board[x][y] = Tile(is_bomb = True)

            for (dx, dy) in DIRECTIONS:
                nx, ny = x+dx, y+dy
                if (0 <= nx < self.board_size and
                0 <= ny < self.board_size and
                not self.board[nx][ny].is_bomb):
                    self.board[nx][ny].adjacent_bombs += 1

    def _print_board(self, print_output=False):
        lines = []
        lines.append('  ' + ' '.join(str(i) for i in range(self.board_size)))
        for row_num, row in enumerate(self.board):
            row_str = f"{row_num} {' '.join(self._tile_to_str(tile) for tile in row)}"
            lines.append(row_str)
        board_str = '\n'.join(lines)
        if print_output:
            print(board_str)
        return board_str

    def _tile_to_str(self, tile: Tile) -> str:
        """Convert a tile to its string representation."""
        if tile.is_flagged:
            return "F"
        if not tile.is_revealed:
            return "."
        else:
            if tile.is_bomb:
                return "*"  # Revealed mine
            elif tile.adjacent_bombs == 0:
                return "_"  # Revealed empty tile
            else:
                return str(tile.adjacent_bombs) # number of mines near

class MineSweeper:
    """
    The gamestate of the game at a point in time.
    - bomb_number
    - flag_number
    """
    def __init__(self, board_size: int, bomb_number: int, model: str, save_dir: str = "minesweeper_games"):
        self.bomb_number = bomb_number
        self.flag_number = bomb_number
        self.board_size = board_size
        self.board = Board(board_size=board_size, number_of_mines=bomb_number)
        self.game_won = False
        self.game_id = str(uuid.uuid4())
        self.game_start_time = datetime.now(timezone.utc)
        self.moves_file = f"./{save_dir}/minesweeper_game_{self.game_id}.jsonl"
        self.model = model

        game_metadata = {
            "type": "game_start",
            "model": self.model,
            "game_id": self.game_id,
            "timestamp": self.game_start_time.isoformat(),
            "board_size": board_size,
            "bomb_number": bomb_number,
            "initial_board": self.board._print_board()
        }
        self._append_to_moves_file(game_metadata)

    def _append_to_moves_file(self, data: dict):
        """Append a move or event to the JSONL file"""
        with open(self.moves_file, 'a') as f:
            f.write(json.dumps(data) + '\n')

    def play_move(self, move_data):
        """ Play the actual game and record the move. """
        move = move_data["move"]
        x, y, is_flag = move

        move_record = {
                "type": "move",
                "move": {
                    "x": x,
                    "y": y,
                    "is_flag": is_flag
                    },
                "explanation":  move_data.get('rationale', ''),
                "flags_remaining": self.flag_number,
                "board_state": self.board._print_board()
        }

        result = self._execute_move(move)
        move_record["sucess"] = result

        self._append_to_moves_file(move_record)

        # If game ends, record that too
        if not result or self.game_won:
            game_end = {
                "type": "game_end",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "game_won": self.game_won,
                "final_board": self.board._print_board()
            }
            self._append_to_moves_file(game_end)
            return False

        return True 


    def _execute_move(self, move):
        x, y, is_flag = move
        tile = self.board.board[x][y]

        if is_flag:
            if self.flag_number <= 0 and not tile.is_flagged:
                print("No flags remaining!")
                return True

            # Toggle flag
            if tile.is_flagged:
                tile.is_flagged = False
                self.flag_number += 1
            else:
                tile.is_flagged = True
                self.flag_number -= 1

            # Check if all bombs are correctly flagged
            self._check_win_condition()
            return True

        # If it's a bomb, game over (you can handle this as needed)
        if tile.is_bomb:
            tile.is_revealed = True  # Reveal the bomb
            print("Game Over: Hit a bomb!")
            return False

        # If already revealed, do nothing
        if tile.is_revealed:
            return True

        nodes = [(x,y)]
        tile.is_revealed = True

        # play the move in case its a bomb say game is cooked
        while nodes:
            [x, y] = nodes.pop() # get first one

            for (dx, dy) in DIRECTIONS:
                nx, ny = x+dx, y+dy
                if (0 <= nx < self.board_size and
                    0 <= ny < self.board_size and
                    not self.board.board[nx][ny].is_bomb):

                    if self.board.board[nx][ny].adjacent_bombs == 0 and not self.board.board[nx][ny].is_revealed:
                        # add this as nodes to keep exploring
                        nodes.append((nx, ny))

                    # mark all the numbers that are near you as seen
                    self.board.board[nx][ny].is_revealed = True

        self._check_win_condition()
        return True

    def _check_win_condition(self):
        all_bombs_flagged = True
        all_safe_revealed = True

        for i in range(self.board_size):
            for j in range(self.board_size):
                tile = self.board.board[i][j]
                if tile.is_bomb:
                    if not tile.is_flagged:
                        all_bombs_flagged = False
                else:
                    if not tile.is_revealed:
                        all_safe_revealed = False

        if all_bombs_flagged or all_safe_revealed:
            self.game_won = True
            print("Congratulations! You've won the game!")
            return True
        
        return False

    def print_board(self) -> str:
        """
        Represents the game board.
        _ = empty space
        . = unexplored space
        * = bomb
        [1-8] = number of bombs near you
        """
        return self.board._print_board()

class MineSweeperRandomPlayer(Player):
    def __init__(self, board_size: int = 10, flag_number: int = 10):
        self.board_size = board_size
        self.flags_remaining = flag_number
        self.all_possible_places = [(i, j) for i in range(self.board_size) for j in range(self.board_size)]

    def get_move(self, board):
        """Randomly select a pair from the board"""

        if len(self.all_possible_places) == 0:
            return -1 # no more moves

        # Check and remove revealed positions from possible moves
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j].is_revealed == True and (i,j) in self.all_possible_places:
                    self.all_possible_places.remove((i,j))

        # 1 in 10 chance of placing a flag if flags are available
        should_place_flag = random.random() < 0.1 and self.flags_remaining > 0

        move = random.sample(self.all_possible_places, 1)[0]
        self.all_possible_places.remove(move)

        if should_place_flag:
            self.flags_remaining -= 1
            return (move[0], move[1], True)

        return (move[0], move[1], False)


class MineSweeperLLMGamer(Player):
    def __init__(self, player_id: str, model: str = "deepseek-ai/DeepSeek-V3"):#"gpt-4o" ):#"claude-3-5-haiku-20241022"):
        super().__init__(player_id)
        self.model = model
        self.provider = create_llm_provider(model)
        self.move_history = []
        self.max_retries = 5
        self.retry_count = 0

    def get_move(self, board) -> str:
        if self.retry_count >= self.max_retries:
            raise Exception("Maximum retries exceeded - model is not providing valid moves")
        prompt = self._construct_prompt(board)
        print(prompt)
        exit()
        response_text = self.provider.get_response(self.model, prompt)
        #print(response_text)

        move = self.get_move_from_response(response_text)

        if isinstance(move, str) and move == "retry":
            self.retry_count += 1
            return "retry"
            
        self.retry_count = 0
        
        move_data = {
                "move": move,
                "rationale": response_text
        }
        self.move_history.append({})
        return move_data


    def get_move_from_response(self, response: str) -> Optional[str]:
        #print(response)
        try:
            # First try line by line for backward compatibility
            lines = response.strip().split('\n')
            for line in reversed(lines):
                if 'MOVE:' in line or '**MOVE**:' in line or '__MOVE__:' in line:
                    clean_line = line.replace('**', '').replace('__', '')
                    after_move = clean_line.split('MOVE:')[1].strip()
                    move_parts = after_move.split(',')
                    if len(move_parts) == 3:
                        x = int(move_parts[0])
                        y = int(move_parts[1])
                        is_flag = move_parts[2].lower().strip() == 'true'
                        return (x, y, is_flag)
    
            # If line-by-line didn't work, try word by word
            # Split on whitespace while preserving punctuation
            words = response.replace('\n', ' ').split()
            
            for i in range(len(words) - 1, -1, -1):
                word = words[i]
                # Clean up the word to check for MOVE
                clean_word = word.replace('**', '').replace('__', '').replace(':', '')
                
                if clean_word == 'MOVE':
                    # Look at the next word(s) for coordinates
                    remaining_text = ' '.join(words[i+1:])
                    # Remove any leading colon
                    remaining_text = remaining_text.lstrip(':').strip()
                    
                    # Try to find three comma-separated numbers
                    for j in range(len(remaining_text)):
                        possible_move = remaining_text[j:j+10]  # reasonable length for coords
                        parts = possible_move.split(',')
                        if len(parts) >= 3:
                            try:
                                x = int(parts[0])
                                y = int(parts[1])
                                is_flag = parts[2].lower().strip().startswith('t')
                                return (x, y, is_flag)
                            except ValueError:
                                continue
                                
            return "retry"
        except Exception as e:
            print(f"Error parsing move: {e}")
            return "retry"


    def _construct_prompt(self, game: MineSweeper):
        """ Construct a prompt for the model. """

        return f"""
You are playing a game of Minesweeper. Here is the current state:

BOARD STATE:
{game.print_board()}

GAME INFO:
- Board size: {game.board_size}x{game.board_size}
- Flags remaining: {game.flag_number}
- Bombs: {game.bomb_number}

BOARD LEGEND:
- _ : Empty revealed space
- . : Unexplored space
- F : Flagged space
- * : Revealed bomb (game over)
- 1-8: Number indicating adjacent bombs

COORDINATE SYSTEM:
The board uses a coordinate system where:
- x represents the ROW number (vertical position, starting from 0 at the top)
- y represents the COLUMN number (horizontal position, starting from 0 at the left)
For example:
- Position (0,0) is always the top-left corner
- Position (board_size-1, 0) is the bottom-left corner
- Position (0, board_size-1) is the top-right corner
- Position (2,3) means: row 2 from top (third row), column 3 from left (fourth column)
NOTE: All coordinates are 0-indexed and must be less than the board size

RULES:
1. The goal is to reveal all safe squares or correctly flag all bombs
2. Numbers show how many bombs are in the adjacent 8 squares
3. You can either reveal a square or place/remove a flag
4. To remove a flag, make a move with flag=true on an already flagged square
5. Game ends if you reveal a bomb

CRITICAL FLAG PLACEMENT RULES:
1. Each number indicates EXACTLY how many bombs are adjacent - no more, no less
2. If a numbered tile shows '1', but already has an adjacent flag, there cannot be another bomb next to it
3. If a numbered tile shows '2' with only one adjacent flag, there MUST be another bomb adjacent
4. Before placing a new flag, verify that it doesn't conflict with the numbers you can see
5. If you see a potential conflict between a flag and revealed numbers, consider removing the flag

ANALYSIS STEPS:
1. First, check all revealed numbers against existing flags
2. Look for obvious conflicts (e.g., a '1' with two adjacent flags)
3. Consider the remaining number of flags vs bombs
4. Only then decide whether to place a new flag or reveal a tile

Provide your next move in this format:
EXPLANATION: (briefly explain your move)
MOVE: x,y,flag
where:
- x,y are coordinates (0-indexed)
- flag is true/false (true = place flag, false = reveal tile)
"""

def main():

    board_size = 10
    player = MineSweeperLLMGamer(str(uuid.uuid4))
    game = MineSweeper(board_size=board_size, bomb_number=10, model=player.model)
    is_game_playing = True

    while is_game_playing:
        print("\nCurrent Board State:")
        game.board._print_board(print_output=True)
        
        while True:
            move = player.get_move(game)
            if isinstance(move, str) and move == "retry":
                print("Invalid move format received, retrying...")
                continue
            break
            
        print(f"{move=}")
        is_game_playing = game.play_move(move)

    print("\nFinal Board State:")
    game.board._print_board(print_output=True)


if __name__ == "__main__":
    main()
