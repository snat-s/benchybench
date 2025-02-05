'use client';

import React from 'react';

// Adjust these interfaces to match your actual game data shape
interface GameRound {
  round_number: number;
  snake_positions: {
    [key: string]: [number, number][]; // modelId -> array of [x, y] positions
  };
  alive: {
    [key: string]: boolean; // modelId -> isAlive
  };
  scores: {
    [key: string]: number;
  };
  width: number;
  height: number;
  apples: [number, number][];
}

interface GameMetadata {
  game_id: string;
  models: { [key: string]: string };
}

interface AsciiSnakePlayerProps {
  rounds: GameRound[];
  metadata: GameMetadata;
  currentRoundIndex: number;
}

/**
 * AsciiSnakePlayer takes all rounds + a current index, and
 * just renders the ASCII board for that round. It does *not*
 * handle any fetching or auto-advancing.
 */
export default function AsciiSnakePlayer({
  rounds,
  metadata,
  currentRoundIndex
}: AsciiSnakePlayerProps) {
  // Basic safety check
  if (!rounds || !rounds.length) {
    return <div style={{ fontFamily: 'monospace' }}>No rounds to display.</div>;
  }

  const currentRound = rounds[currentRoundIndex];

  // Build an ASCII representation of the current round's board.
  const renderBoardAscii = (round: GameRound) => {
    const { width, height, apples, snake_positions, alive } = round;
    // Initialize a board filled with periods.
    const board: string[][] = Array.from({ length: height }, () =>
      Array.from({ length: width }, () => '.')
    );

    // Place the apples
    apples.forEach(([ax, ay]) => {
      if (ay >= 0 && ay < height && ax >= 0 && ax < width) {
        board[ay][ax] = 'A';
      }
    });

    // Place the snakes – sort keys so that "1" comes before "2" (etc.)
    const snakeIds = Object.keys(snake_positions).sort();
    snakeIds.forEach((snakeId, index) => {
      if (!alive[snakeId]) return; // skip if dead
      const positions = snake_positions[snakeId];
      positions.forEach(([x, y], posIndex) => {
        if (x >= 0 && x < width && y >= 0 && y < height) {
          // Head is marked by the snake index (1, 2, ...)
          board[y][x] = posIndex === 0 ? (index + 1).toString() : 'T';
        }
      });
    });

    // Build the string: rows from top (height - 1) down to 0
    let boardStr = '';
    for (let y = height - 1; y >= 0; y--) {
      boardStr += y.toString().padStart(2, ' ') + ' ' + board[y].join(' ') + '\n';
    }
    // Add x-axis labels
    boardStr += '   ' + Array.from({ length: width }, (_, i) => i.toString()).join(' ') + '\n';
    return boardStr;
  };

  const boardAscii = renderBoardAscii(currentRound);

  // Display model names in the title if desired
  const models = metadata.models;
  // e.g. "ModelName1 (1) vs ModelName2 (2)"
  const titleAscii = `${models['1']} (1) vs ${models['2']} (2)`;

  return (
    <div className="font-mono border border-gray-200 p-6 hover:shadow-lg transition-shadow inline-block min-w-fit">
      {/* Game Title */}
      <div className="whitespace-pre-wrap break-all max-w-full text-sm mb-4 text-center h-[4.6em] line-clamp-3 overflow-hidden">
        {titleAscii}
      </div>

      {/* ASCII Board */}
      <div className="whitespace-pre text-[11px] leading-[1.15] text-center">
        {boardAscii}
      </div>
    </div>
  );
}
