'use client';

import { useState, useEffect } from 'react';

interface Move {
  move: string;
  rationale: string;
}

interface Round {
  round_number: number;
  snake_positions: { [key: string]: number[][] };
  alive: { [key: string]: boolean };
  scores: { [key: string]: number };
  width: number;
  height: number;
  apples: number[][];
  move_history?: Array<{ [key: string]: Move }>;
}

interface GameData {
  metadata: {
    game_id: string;
    start_time: string;
    end_time: string;
    models: { [key: string]: string };
    game_result: { [key: string]: string };
    final_scores: { [key: string]: number };
    death_info?: any;
    max_rounds: number;
    actual_rounds: number;
  };
  rounds: Round[];
}

// A simple helper component to render the board as ASCII art.
// It draws each cell – mark apples as "A" and any snake cell with its snake id.
function AsciiBoard({ boardState }: { boardState: Round }) {
  const { width, height, snake_positions, apples } = boardState;
  // Create a matrix filled with a background character (here a dot)
  const board = Array.from({ length: height }, () => Array(width).fill('.'));

  // Place apple markers.
  apples.forEach(([r, c]) => {
    if (r >= 0 && r < height && c >= 0 && c < width) {
      board[r][c] = 'A';
    }
  });

  // Place snake positions (e.g. "1" or "2")
  if (snake_positions) {
    Object.entries(snake_positions).forEach(([snakeId, positions]) => {
      positions.forEach(([r, c]) => {
        if (r >= 0 && r < height && c >= 0 && c < width) {
          board[r][c] = snakeId;
        }
      });
    });
  }
  
  const boardString = board.map(row => row.join(' ')).join('\n');
  return (
    <pre style={{ background: "#f0f0f0", padding: "10px" }}>
      {boardString}
    </pre>
  );
}

export default function MatchReplay({ data }: { data: GameData }) {
  const { metadata, rounds } = data;
  // currentStep indicates which round from the game data is shown.
  const [currentStep, setCurrentStep] = useState(0);
  // Playing flag enables auto-advancing every second.
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (playing) {
      timer = setInterval(() => {
        setCurrentStep(prev => {
          if (prev < rounds.length - 1) {
            return prev + 1;
          } else {
            setPlaying(false);
            return prev;
          }
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [playing, rounds.length]);

  const currentRound = rounds[currentStep];
  // Get the move information from the current round.
  // If no move history exists in the round, moveInfo will be null.
  const moveInfo =
    currentRound.move_history && currentRound.move_history.length > 0
      ? currentRound.move_history[currentRound.move_history.length - 1]
      : null;

  const handleBack = () => {
    setPlaying(false);
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const handleForward = () => {
    setPlaying(false);
    setCurrentStep(prev => Math.min(prev + 1, rounds.length - 1));
  };

  const togglePlay = () => {
    setPlaying(!playing);
  };

  return (
    <div>
      {/* Title with the two model names */}
      <h1 style={{ textAlign: "center" }}>
        {metadata.models["1"]} vs. {metadata.models["2"]}
      </h1>

      {/* Board at the top */}
      <AsciiBoard boardState={currentRound} />

      {/* Navigation buttons */}
      <div style={{ textAlign: "center", marginTop: "10px" }}>
        <button onClick={handleBack}>Back</button>
        <button onClick={togglePlay} style={{ margin: "0 10px" }}>
          {playing ? "Pause" : "Play"}
        </button>
        <button onClick={handleForward}>Forward</button>
      </div>

      {/* Two columns for the move information */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: "20px"
        }}
      >
        <div style={{ width: "48%" }}>
          <h2>{metadata.models["1"]}</h2>
          <p>
            <strong>Move:</strong> {moveInfo ? moveInfo["1"].move : "No move"}
          </p>
          <p>
            <strong>Rationale:</strong> {moveInfo ? moveInfo["1"].rationale : ""}
          </p>
        </div>
        <div style={{ width: "48%" }}>
          <h2>{metadata.models["2"]}</h2>
          <p>
            <strong>Move:</strong> {moveInfo ? moveInfo["2"].move : "No move"}
          </p>
          <p>
            <strong>Rationale:</strong> {moveInfo ? moveInfo["2"].rationale : ""}
          </p>
        </div>
      </div>
    </div>
  );
}