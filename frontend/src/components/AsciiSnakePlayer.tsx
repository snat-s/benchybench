'use client'

import { useState, useEffect, JSX } from 'react'

interface GameRound {
  round_number: number;
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

interface GameMetadata {
  game_id: string;
  models: { [key: string]: string };
  game_result: { [key: string]: string };
  final_scores: { [key: string]: number };
  // Other metadata fields as needed.
}

interface GameData {
  metadata: GameMetadata;
  rounds: GameRound[];
}

interface AsciiSnakeGameProps {
  // Instead of gameId, we now accept full game data.
  initialGameData: GameData;
}

export default function AsciiSnakeGame({ initialGameData }: AsciiSnakeGameProps) {
  const [gameData] = useState<GameData>(initialGameData)
  const [currentRoundIdx, setCurrentRoundIdx] = useState<number>(0)

  // Animate through rounds at a slow interval. When the animation finishes, restart.
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentRoundIdx((prev) => (prev + 1) % gameData.rounds.length)
    }, 1000) // Change round every 1 second

    return () => clearInterval(interval)
  }, [gameData])

  const currentRound = gameData.rounds[currentRoundIdx]

  // Build an ASCII representation of the current round's board.
  const renderBoardAscii = (round: GameRound) => {
    const { width, height, apples, snake_positions, alive } = round
    // Initialize a board filled with periods, but now with objects containing char and class
    const board: Array<Array<{char: string, class?: string}>> = Array.from({ length: height }, () =>
      Array.from({ length: width }, () => ({char: '.'}))
    )

    // Place the apples
    apples.forEach(([ax, ay]) => {
      if (ay >= 0 && ay < height && ax >= 0 && ax < width)
        board[ay][ax] = {char: 'A', class: 'bg-yellow-200 text-black'} // Yellow background
    })

    // Place the snakes
    const snakeIds = Object.keys(snake_positions).sort()
    snakeIds.forEach((snakeId, index) => {
      if (!alive[snakeId]) return
      const positions = snake_positions[snakeId]
      const snakeClass = snakeId === '1' ? 'bg-green-200 text-black' : 'bg-red-200 text-black'
      positions.forEach((pos, posIndex) => {
        const [x, y] = pos
        if (x >= 0 && x < width && y >= 0 && y < height) {
          board[y][x] = {
            char: posIndex === 0 ? (index + 1).toString() : 'T',
            class: snakeClass
          }
        }
      })
    })

    // Build the string with spans for colored characters
    const boardJsx: JSX.Element[] = []
    for (let y = height - 1; y >= 0; y--) {
      // Row number (uncolored)
      boardJsx.push(<span key={`row-${y}`}>{y.toString().padStart(2, ' ') + ' '}</span>)
      // Board cells
      board[y].forEach((cell, x) => {
        boardJsx.push(
          <span key={`${y}-${x}`} className={cell.class}>
            {cell.char + ' '}
          </span>
        )
      })
      boardJsx.push(<br key={`br-${y}`} />)
    }
    // Add x-axis labels (uncolored)
    boardJsx.push(
      <span key="x-axis">
        {'   ' + Array.from({ length: width }, (_, i) => i.toString()).join(' ') + '\n'}
      </span>
    )
    return boardJsx
  }

  const boardJsx = renderBoardAscii(currentRound)
  const models = gameData.metadata.models
  const titleAscii = (
    <>
      <span className="bg-green-200 text-black text-xs">{models['1']}</span>
      {' (1) vs '}
      <span className="bg-red-200 text-black text-xs">{models['2']}</span>
      {' (2)'}
    </>
  )

  return (
      <div className="font-mono border border-gray-200 p-6 hover:shadow-lg transition-shadow inline-block min-w-fit">
        {/* Game Title */}
        <div className="whitespace-pre-wrap break-all max-w-full text-sm mb-4 text-center h-[4.6em] line-clamp-3 overflow-hidden">
          {titleAscii}
        </div>
        {/* ASCII Board */}
        <div className="whitespace-pre text-[11px] leading-[1.15] text-center">
          {boardJsx}
        </div>
        <hr className="my-4" />
        {/* Link to match */}
        <div className="text-center">
          <a 
            href={`/match/${gameData.metadata.game_id}`}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            View match
          </a>
        </div>
      </div>
  )
}