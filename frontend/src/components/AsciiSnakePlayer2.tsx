'use client';

import React, { JSX } from 'react';

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
    // Initialize a board filled with periods, but now with objects containing char and class
    const board: Array<Array<{char: string, class?: string}>> = Array.from({ length: height }, () =>
      Array.from({ length: width }, () => ({char: '.'}))
    );

    // Place the apples
    apples.forEach(([ax, ay]) => {
      if (ay >= 0 && ay < height && ax >= 0 && ax < width) {
        board[ay][ax] = {char: 'A', class: 'bg-yellow-200 text-black'}; // Yellow background
      }
    });

    // Place the snakes
    const snakeIds = Object.keys(snake_positions).sort();
    snakeIds.forEach((snakeId, index) => {
      if (!alive[snakeId]) return;
      const positions = snake_positions[snakeId];
      const snakeClass = snakeId === '1' ? 'bg-green-200 text-black' : 'bg-red-200 text-black';
      positions.forEach(([x, y], posIndex) => {
        if (x >= 0 && x < width && y >= 0 && y < height) {
          board[y][x] = {
            char: posIndex === 0 ? (index + 1).toString() : 'T',
            class: snakeClass
          };
        }
      });
    });

    // Build the string with spans for colored characters
    const boardJsx: JSX.Element[] = [];
    for (let y = height - 1; y >= 0; y--) {
      // Row number (uncolored)
      boardJsx.push(<span key={`row-${y}`}>{y.toString().padStart(2, ' ') + ' '}</span>);
      // Board cells
      board[y].forEach((cell, x) => {
        boardJsx.push(
          <span key={`${y}-${x}`} className={cell.class}>
            {cell.char + ' '}
          </span>
        );
      });
      boardJsx.push(<br key={`br-${y}`} />);
    }
    // Add x-axis labels (uncolored)
    boardJsx.push(
      <span key="x-axis">
        {'   ' + Array.from({ length: width }, (_, i) => i.toString()).join(' ') + '\n'}
      </span>
    );
    return boardJsx;
  };

  const boardJsx = renderBoardAscii(currentRound);

  // Display model names in the title if desired
  const models = metadata.models;
  // e.g. "ModelName1 (1) vs ModelName2 (2)"
  const titleJsx = (
    <>
      <span className="bg-green-200 text-black text-xs">{models['1']}</span>
      {' (1) vs '}
      <span className="bg-red-200 text-black text-xs">{models['2']}</span>
      {' (2)'}
    </>
  );

  return (
    <div className="font-mono border border-gray-200 p-6 hover:shadow-lg transition-shadow inline-block min-w-fit">
      {/* Game Title */}
      <div className="whitespace-pre-wrap break-all max-w-full text-sm mb-4 text-center line-clamp-3 overflow-hidden">
        {titleJsx}
      </div>

      {/* ASCII Board */}
      <div className="whitespace-pre text-[11px] leading-[1.15] text-center">
        {boardJsx}
      </div>
    </div>
  );
}
