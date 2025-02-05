'use client';

import { useState, useEffect } from 'react';
import AsciiSnakePlayer from '@/components/AsciiSnakePlayer2';

interface MoveHistoryEntry {
  [modelId: string]: {
    move: string;
    rationale: string;
  };
}

interface RoundData {
  round_number: number;
  move_history?: MoveHistoryEntry[];
  snake_positions: {
    [key: string]: [number, number][];
  };
  alive: {
    [key: string]: boolean;
  };
  scores: {
    [key: string]: number;
  };
  width: number;
  height: number;
  apples: [number, number][];
}

interface GameData {
  metadata: {
    game_id: string;
    models: Record<string, string>;
    game_result: Record<string, string>;
    death_info: Record<string, { reason: string }>;
  };
  rounds: RoundData[];
}

interface GameViewerProps {
  gameData: GameData;
}

/**
 * GameViewer displays:
 *  - The ASCII snake board at the top (via AsciiSnakePlayer)
 *  - Next/Back/Play controls
 *  - Two columns with model #1 and model #2 info
 *  - Rationales for the current round
 */
export default function GameViewer({ gameData }: GameViewerProps) {
  const { rounds, metadata } = gameData;
  
  // Current index in the rounds array
  const [currentRoundIndex, setCurrentRoundIndex] = useState(0);
  // Whether auto-play is active
  const [isPlaying, setIsPlaying] = useState(false);

  // We'll keep a simple useEffect to handle auto-play
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentRoundIndex((prev) => {
          // Advance one round if possible, else stop
          if (prev < rounds.length - 1) {
            return prev + 1;
          } else {
            setIsPlaying(false);
            return prev;
          }
        });
      }, 1000); // 1 second per move (adjust as needed)
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, rounds.length]);

  // Handlers for back/forward
  const handleBack = () => {
    setIsPlaying(false);
    setCurrentRoundIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleForward = () => {
    setIsPlaying(false);
    setCurrentRoundIndex((prev) => Math.min(prev + 1, rounds.length - 1));
  };

  const handlePlayPause = () => {
    setIsPlaying((prev) => !prev);
  };

 
  // Get the NEXT round's move history (for showing upcoming rationale)
  const nextRound = rounds[currentRoundIndex + 1] || {};
  const nextMoveHistory = nextRound.move_history || [];
  // We want the last move in that history
  const nextLastMove = nextMoveHistory[nextMoveHistory.length - 1] || {};

  const modelOneId = '1';
  const modelTwoId = '2';
  const modelOneName = metadata.models[modelOneId];
  const modelTwoName = metadata.models[modelTwoId];

  // Extract rationale/move for each model from the NEXT round
  const modelOneRationale = nextLastMove[modelOneId]?.rationale || 'No future move available';
  const modelTwoRationale = nextLastMove[modelTwoId]?.rationale || 'No future move available';
  const modelOneChoice = nextLastMove[modelOneId]?.move || 'No future move available';
  const modelTwoChoice = nextLastMove[modelTwoId]?.move || 'No future move available';

  // Add helper function to get game outcome message
  const getGameOutcomeMessage = () => {
    const { game_result, death_info } = metadata;
    const messages = [];

    for (const [modelId, result] of Object.entries(game_result)) {
      const modelName = metadata.models[modelId];
      const resultText = result === 'won' ? 'Winner' : 'Lost';
      let message = `${modelName}: ${resultText}`;
      
      // Add death reason if available
      if (death_info?.[modelId]) {
        message += ` (${death_info[modelId].reason})`;
      }
      
      messages.push(message);
    }

    return messages;
  };

  return (
    <div className="container mx-auto max-w-6xl px-4">
      {/* Game outcome banner - show only when game is finished */}
      {currentRoundIndex === rounds.length - 1 && (
        <div className="p-4 mb-4 rounded text-center">
          <h2 className="text-xl font-bold mb-2">Game Over</h2>
          {getGameOutcomeMessage().map((message, index) => (
            <div key={index} className="text-lg">
              {message}
            </div>
          ))}
        </div>
      )}

      {/* The ASCII snake board for the current round (rendered by the child) */}
      <div className="flex justify-center">
        <AsciiSnakePlayer
          rounds={rounds}           // pass all rounds
          metadata={metadata}       // pass metadata for model names, etc.
          currentRoundIndex={currentRoundIndex}
        />
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-4 my-4">
        <button onClick={handleBack}>Back</button>
        <button onClick={handlePlayPause}>
          {isPlaying ? 'Pause' : 'Play'}
        </button>
        <button onClick={handleForward}>Forward</button>
      </div>

      {/* Rationales */}
      <div className="border border-gray-300 p-4 rounded max-w-4xl mx-auto">
        <h3 className="text-center pb-2">Round {currentRoundIndex}:</h3>
        <div className="grid grid-cols-2 gap-5">
          <div>
            <h4>Model #1: {modelOneName}</h4>
            <strong>Choice: {modelOneChoice}</strong>
            <br />
            <strong>Rationale:</strong>
            <p>{modelOneRationale}</p>
          </div>
          <div>
            <h4>Model #2: {modelTwoName}</h4>
            <strong>Choice: {modelTwoChoice}</strong>
            <br />
            <strong>Rationale:</strong>
            <p>{modelTwoRationale}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
