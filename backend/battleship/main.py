"""
Battleship for llms.
"""
import random
import uuid

from typing import Tuple
from dataclasses import dataclass

SHIPS = {
    "CARRIER": 5,
    "BATTLESHIP": 4,
    "CRUISER": 3,
    "SUBMARINE": 3,
    "DESTROYER": 2,
}
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),           (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

class BattleShip:
    """
    The game logic for BattleShip, only checks if it is valid moves.
    """
    def __init__(self):
        pass
    def _():

class GameState:
    """
    Class that tracks the game state of both LLMs
    """
    def __init__(self):
        self.players = []
        self.personal_boards = []
        self.opponent_boards = []
        self._init_state()

    def _init_state(self):
        for _ in range(2):
            board = [[Tile() for _ in range(10)] for _ in range(10)]
            self.personal_boards.append(board)
            self.opponent_boards.append(board)

class Player:
    """
    Base class where both LLM players and human players come from.
    """ 
    def __init__(self, battle_ship_id: str):
        pass

    def get_move(self, game_state: GameState):
        pass

@dataclass
class Tile:
    is_occupied: bool = False
    is_hit: bool = False
    is_ship: bool = False


def check_border_constraint_in_init(possible_position: Tuple[int, int], ship_size: int, direction: int, player: int, game_state: GameState) -> Tuple[int, int]:
        x, y = possible_position
        if direction == 0:  # Horizontal
            if y + ship_size > 10:
                return (-1, -1)
            for i in range(ship_size):
                if game_state.personal_boards[player][x][y + i].is_occupied:
                    return (-1, -1)
        else:  # Vertical
            if x + ship_size > 10:
                return (-1, -1)
            for i in range(ship_size):
                if game_state.personal_boards[player][x + i][y].is_occupied:
                    return (-1, -1)
        return possible_position


def get_board_state_as_string(board):
    """
    Returns the state of the board as a string for debugging purposes.
    Symbols:
    - 'S': Ship not hit
    - 'X': Ship hit
    - 'O': Hit but no ship
    - '#': Occupied tile (no ship)
    - '.': Empty tile
    """
    # Column headers (A-J)
    board_str = "   " + " ".join([chr(65 + i) for i in range(10)]) + "\n"
    
    for row_num, row in enumerate(board, start=1):
        # Row number (1-10)
        board_str += f"{row_num:2} "
        for tile in row:
            if tile.is_ship and tile.is_hit:
                board_str += "X "  # Ship hit
            elif tile.is_ship:
                board_str += "S "  # Ship not hit
            elif tile.is_hit:
                board_str += "O "  # Hit but no ship
            elif tile.is_occupied:
                board_str += "# "  # Occupied tile (no ship)
            else:
                board_str += ". "  # Empty tile
        board_str += "\n"
    return board_str

class LLMPlayer(Player):
    def __init__(self, battle_ship_id: str, player: int, model_name:str = "gpt4o-mini"):
        self.battle_ship_id = battle_ship_id
        self.player = player
        self.provider = create_llm_provider(model_name)
        self.model_name = model_name

    def get_move(self, game_state: GameState):
        prompt = self._construct_prompt(game_state)
        response_text = self.provider.get_response(self.model, prompt)

    def _construct_prompt(self, game_state: GameState) -> str:
        return f"""
        """

class RandomPlayer(Player):
    """
    Random Player to debug if the game is working correctly or not
    """
    def __init__(self, battle_ship_id: str, player: int):
        self.player = player
        self.battle_ship_id = battle_ship_id

    def _init_boats(self, game_state: GameState):
        """
        Put the boats randomly on the board
        """
        for ship, size in SHIPS.items():
            position = (-1, -1)
            while position == (-1, -1):
                direction = random.randint(0, 1)  # 0 for horizontal, 1 for vertical
                if direction == 0:  # Horizontal
                    x = random.randint(0, 9)
                    y = random.randint(0, 10 - size)
                else:  # Vertical
                    x = random.randint(0, 10 - size)
                    y = random.randint(0, 9)
                position = check_border_constraint_in_init((x,y), size, direction, self.player, game_state)

            # ship placement
            ship_positions = []
            for i in range(size):
                if direction == 0:  # Horizontal
                    game_state.personal_boards[self.player][x][y + i].is_ship = True
                    game_state.personal_boards[self.player][x][y + i].is_occupied = True
                    ship_positions.append((x, y + i))
                else:  # Vertical
                    game_state.personal_boards[self.player][x + i][y].is_ship = True
                    game_state.personal_boards[self.player][x + i][y].is_occupied = True
                    ship_positions.append((x + i, y))

        
            # you also can't have a boat directly at your sides 
            for ship_x, ship_y in ship_positions:
                for direction in DIRECTIONS:
                    adj_x, adj_y = ship_x + direction[0], ship_y + direction[1]
                    if 0 <= adj_x < 10 and 0 <= adj_y < 10:
                        # Only mark as occupied if it's not already a ship but really doesn't matter because already marked as occupied
                        if not game_state.personal_boards[self.player][adj_x][adj_y].is_ship:
                            game_state.personal_boards[self.player][adj_x][adj_y].is_occupied = True

    def get_move(self, game_state: GameState):
        opponent = 1 - self.player

        valid_positions = []
        for x in range(10):
            for y in range(10):
                if not game_state.personal_boards[opponent][x][y].is_hit:
                    valid_positions.append((x, y))

        if not valid_positions:
            return None

        return random.choice(valid_positions)


def main(): 
    random_player_1 = RandomPlayer(str(uuid.uuid1()), 0)
    game_state = GameState()
    random_player_1._init_boats(game_state)
    print("Player 0's Board:")
    print(get_board_state_as_string(game_state.personal_boards[0]))


if __name__ == "__main__":
    main()
