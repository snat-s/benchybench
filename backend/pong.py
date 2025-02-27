import random
from typing import Dict, Tuple, List
from datetime import datetime
import os
import json
import uuid
import argparse
from collections import deque
from llm_providers import create_llm_provider

# Directions
UP = "UP"
DOWN = "DOWN"
STAY = "STAY"
VALID_MOVES = {UP, DOWN, STAY}

class Paddle:
    """Represents a player's paddle"""
    def __init__(self, y: int, size: int = 3):
        self.y = y  # vertical center position
        self.size = size
        self.score = 0

class Ball:
    """Represents the game ball"""
    def __init__(self, x: int, y: int, dx: int, dy: int):
        self.x = x
        self.y = y
        self.dx = dx  # horizontal direction (-1 = left, 1 = right)
        self.dy = dy  # vertical direction

class GameState:
    """Snapshot of the Pong game state"""
    def __init__(self,
                 frame: int,
                 paddle_left: Paddle,
                 paddle_right: Paddle,
                 ball: Ball,
                 width: int,
                 height: int,
                 state_history = None):
        self.frame = frame
        self.paddle_left = paddle_left
        self.paddle_right = paddle_right
        self.ball = ball
        self.width = width
        self.height = height
        self.state_history = state_history if state_history is not None else deque(maxlen=3)

    def to_dict(self) -> dict:
        """Convert the game state to a JSON-serializable dictionary"""
        return {
            "frame": self.frame,
            "paddle_left": {
                "y": self.paddle_left.y,
                "size": self.paddle_left.size,
                "score": self.paddle_left.score
            },
            "paddle_right": {
                "y": self.paddle_right.y,
                "size": self.paddle_right.size,
                "score": self.paddle_right.score
            },
            "ball": {
                "x": self.ball.x,
                "y": self.ball.y,
                "dx": self.ball.dx,
                "dy": self.ball.dy,
            },
            "width": self.width,
            "height": self.height
        }

    def print_board(self) -> str:
        """Text-based representation of the game state with borders"""
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        # Draw top and bottom borders
        for x in range(self.width):
            board[0][x] = '-'
            board[self.height-1][x] = '-'

        # Draw paddles
        for dy in range(-self.paddle_left.size//2, self.paddle_left.size//2+1):
            y = self.paddle_left.y + dy
            if 0 <= y < self.height:
                board[y][0] = '|'  # Left paddle
        for dy in range(-self.paddle_right.size//2, self.paddle_right.size//2+1):
            y = self.paddle_right.y + dy
            if 0 <= y < self.height:
                board[y][-1] = '|'  # Right paddle

        # Draw ball
        if 0 <= self.ball.x < self.width and 0 <= self.ball.y < self.height:
            board[self.ball.y][self.ball.x] = 'O'

        # Convert to string
        board_str = "\n".join([''.join(row) for row in board])
        score_str = f"Left: {self.paddle_left.score} | Right: {self.paddle_right.score}"
        return f"{score_str}\n{board_str}"

class Player:
    """Base class for Pong players"""
    def __init__(self, side: str):
        self.side = side  # 'left' or 'right'

    def get_move(self, game_state: GameState) -> dict:
        raise NotImplementedError

class LLMPlayer(Player):
    """LLM-controlled Pong player"""
    def __init__(self, side: str, model: str = "gpt-4o-mini"):
        super().__init__(side)
        self.model = model
        self.provider = create_llm_provider(model)
        self.move_history = []

    def get_move(self, game_state: GameState) -> dict:
        prompt = self._construct_prompt(game_state)
        full_response = self.provider.get_response(self.model, prompt)
        move = self._parse_response(full_response)
        return {"move": move, "full_response": full_response}

    def _construct_prompt(self, game_state: GameState) -> str:

        history_str = ""
        if game_state.state_history:
            history_str = "Previous states:\n"
            for i, state in enumerate(game_state.state_history):
                            history_str += f"\nState {i+1}:\n{state.print_board()}\n"
        with open("history.txt", 'a') as f:
            f.write(history_str)
        #print("-----THIS IS HISTORY-----\n", history_str, "\n-----THIS WAS HISTORY-----")
        #print(history_str)
        #input()
        return f"""
        You are controlling a Pong paddle on the {self.side} side of the board. Your goal is to prevent the ball (O) from getting past your paddle (|) while trying to score against your opponent.

        {history_str}
        Current Game State:
        {game_state.print_board()}

        Game Rules:
        1. This is turn-based - after you move, the ball will move one step
        2. The ball (O) moves diagonally and bounces off walls and paddles
        3. You score a point when the ball gets past your opponent's paddle
        4. Your paddle is {game_state.paddle_left.size} units tall

        Your Move Options:
        - Type 'UP' to move your paddle up one space
        - Type 'DOWN' to move your paddle down one space
        - Type 'STAY' to keep your paddle in its current position

        Please only answer with one of the following: UP, DOWN, or STAY
        """

    def _parse_response(self, response: str) -> str:
        #print(response)
        words = response.strip().split()
        # Scan backwards through words
        for word in reversed(words):
            if word.upper() in VALID_MOVES:
                #print(word.upper())
                return word.upper()
        return STAY

class PongGame:
    """Manages the Pong game state and logic"""
    def __init__(self, width=40, height=20, max_score=3):
        self.width = width
        self.height = height
        self.max_score = max_score
        self.state_history = []
        self.game_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.move_history = []

        self.reset_game()


    def reset_game(self):
        self.paddle_left = Paddle(self.height//2)
        self.paddle_right = Paddle(self.height//2)
        self.ball = Ball(self.width//2, self.height//2,
                        random.choice([-1, 1]),
                        random.choice([-1, 1]))
        self.frame = 0
        self.game_over = False
        self.winner = None
        self.state_history.clear()

    def save_game_state(self):
        """Save the complete game state to a JSON file"""
        # Ensure the output directory exists
        os.makedirs('completed_games', exist_ok=True)

        # Create metadata
        metadata = {
            "game_id": self.game_id,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_frames": self.frame,
            "final_scores": {
                "left": self.paddle_left.score,
                "right": self.paddle_right.score
            },
            "winner": self.winner,
            "board_dimensions": {
                "width": self.width,
                "height": self.height
            },
            "max_score": self.max_score
        }

        # Create game history
        game_history = {
            "frames": [state.to_dict() for state in self.state_history],
            "move_history": self.move_history
        }

        # Combine all data
        game_data = {
            "metadata": metadata,
            "history": game_history
        }

        # Save to file
        filename = f"pong_game_{self.game_id}.json"
        with open(f"completed_games/{filename}", "w") as f:
            json.dump(game_data, f, indent=2)

        print(f"Game state saved to completed_games/{filename}")

    def _save_current_state(self):
        """Creates a snapshot of the current game state"""
        current_state = GameState(
            frame=self.frame,
            paddle_left=Paddle(self.paddle_left.y, self.paddle_left.size),
            paddle_right=Paddle(self.paddle_right.y, self.paddle_right.size),
            ball=Ball(self.ball.x, self.ball.y, self.ball.dx, self.ball.dy),
            width=self.width,
            height=self.height,
            state_history=None  # Don't include history in the snapshot
        )
        # Copy scores
        current_state.paddle_left.score = self.paddle_left.score
        current_state.paddle_right.score = self.paddle_right.score
        return current_state

    def update(self, left_move: dict, right_move: dict):
        """Update game state with player moves"""
        if self.game_over:
            return

        # Record the moves
        self.move_history.append({
            "frame": self.frame,
            "moves": {
                "left": {
                    "action": left_move["move"],
                    "model_response": left_move["full_response"],
                },
                "right": {
                    "action": right_move["move"],
                    "model_response": right_move["full_response"]
                }
            }
        })

        # Save current state
        current_state = GameState(
            self.frame, Paddle(self.paddle_left.y, self.paddle_left.size),
            Paddle(self.paddle_right.y, self.paddle_right.size),
            Ball(self.ball.x, self.ball.y, self.ball.dx, self.ball.dy),
            self.width, self.height)
        current_state.paddle_left.score = self.paddle_left.score
        current_state.paddle_right.score = self.paddle_right.score
        self.state_history.append(current_state)

        # Move paddles
        self._move_paddle(self.paddle_left, left_move["move"])
        self._move_paddle(self.paddle_right, right_move["move"])

        # Update ball position
        self.ball.x += self.ball.dx
        self.ball.y += self.ball.dy

        # Ball collisions
        self._handle_wall_collisions()
        self._handle_paddle_collisions()

        # Score checking
        self._check_score()

        self.frame += 1

        # if game over
        if self.game_over:
            self.save_game_state()

    def _move_paddle(self, paddle: Paddle, move: str):
        # Calculate paddle edges considering its size
        paddle_top = paddle.y - paddle.size // 2
        paddle_bottom = paddle.y + paddle.size // 2

        if move == UP and paddle_top > 0:
            paddle.y = max(paddle.size // 2, paddle.y - 1)
        elif move == DOWN and paddle_bottom < self.height - 1:
            paddle.y = min(self.height - 1 - paddle.size // 2, paddle.y + 1)

    def _handle_wall_collisions(self):
        if self.ball.y <= 0 or self.ball.y >= self.height-1:
            self.ball.dy *= -1

    def _handle_paddle_collisions(self):
            # First check left paddle collision (at x=0)
            if 0 <= self.ball.x <= 1:  # Check both positions 0 and 1
                if self._paddle_contact(self.paddle_left):
                    self.ball.dx = 1  # Force ball to move right
                    self.ball.x = 1  # Push ball away from paddle


            # Then check right paddle collision (at x=width-1)
            if self.width-2 <= self.ball.x <= self.width-1:
                if self._paddle_contact(self.paddle_right):
                    self.ball.dx = -1  # Force ball to move left
                    self.ball.x = self.width-2  # Push ball away from paddle

    def _paddle_contact(self, paddle: Paddle) -> bool:
        return abs(self.ball.y - paddle.y) <= paddle.size//2

    def _check_score(self):
        if self.ball.x < 0:
            self.paddle_right.score += 1
            self._reset_ball()
        elif self.ball.x >= self.width:
            self.paddle_left.score += 1
            self._reset_ball()

        if self.paddle_left.score >= self.max_score:
            self.game_over = True
            self.winner = 'left'
        elif self.paddle_right.score >= self.max_score:
            self.game_over = True
            self.winner = 'right'

    def _reset_ball(self):
        # Reset ball position
        self.ball = Ball(self.width//2, self.height//2,
                        random.choice([-1, 1]),
                        random.choice([-1, 1]))
        # Reset paddles to center after each point
        self.paddle_left.y = self.height // 2
        self.paddle_right.y = self.height // 2

def main():
    parser = argparse.ArgumentParser(description='LLM Pong Tournament')
    parser.add_argument('--left', type=str, required=True, help='Left paddle model')
    parser.add_argument('--right', type=str, required=True, help='Right paddle model')
    args = parser.parse_args()

    game = PongGame()
    left_player = LLMPlayer('left', args.left)
    right_player = LLMPlayer('right', args.right)

    while not game.game_over:
        print(f"Player: {args.left}")
        left_move = left_player.get_move(GameState(
            game.frame,
            game.paddle_left,
            game.paddle_right,
            game.ball,
            game.width,
            game.height,
            state_history=list(game.state_history),#[-3:] if game.state_history else []),
        ))
        print(f"Player: {args.right}")
        right_move = right_player.get_move(GameState(
            game.frame,
            game.paddle_left,
            game.paddle_right,
            game.ball,
            game.width,
            game.height,
            state_history=list(game.state_history[-3:] if game.state_history else []),
        ))

        game.update(left_move, right_move)
        print(f"\nFrame {game.frame}")
        print(GameState(game.frame, game.paddle_left,
                       game.paddle_right, game.ball,
                       game.width, game.height).print_board())

    print(f"Game Over! Winner: {game.winner}")
    print(f"Final score - Left: {game.paddle_left.score}, Right: {game.paddle_right.score}")

if __name__ == "__main__":
    main()
