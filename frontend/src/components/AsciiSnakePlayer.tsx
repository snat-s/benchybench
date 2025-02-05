'use client'

import { useState, useEffect } from 'react'

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
    // Initialize a board filled with periods.
    const board: string[][] = Array.from({ length: height }, () =>
      Array.from({ length: width }, () => '.')
    )

    // Place the apples
    apples.forEach(([ax, ay]) => {
      if (ay >= 0 && ay < height && ax >= 0 && ax < width)
        board[ay][ax] = 'A'
    })

    // Place the snakes – sort keys so that "1" comes before "2" (so numbering is consistent)
    const snakeIds = Object.keys(snake_positions).sort()
    snakeIds.forEach((snakeId, index) => {
      // Only show the snake if it is still alive in this round.
      if (!alive[snakeId]) return
      const positions = snake_positions[snakeId]
      positions.forEach((pos, posIndex) => {
        const [x, y] = pos
        if (x >= 0 && x < width && y >= 0 && y < height) {
          // Head is marked by the snake index (starting at 1); all other parts as "T"
          board[y][x] = posIndex === 0 ? (index + 1).toString() : 'T'
        }
      })
    })

    // Build the string: rows from top (height - 1) to bottom (0)
    let boardStr = ''
    for (let y = height - 1; y >= 0; y--) {
      // Row number padded to 2 characters (as in Python f"{y:2d}")
      boardStr += y.toString().padStart(2, ' ') + ' ' + board[y].join(' ') + '\n'
    }
    // Add x-axis labels
    boardStr += '   ' + Array.from({ length: width }, (_, i) => i.toString()).join(' ') + '\n'
    return boardStr
  }

  const boardAscii = renderBoardAscii(currentRound)
  const models = gameData.metadata.models
  const titleAscii = `${models['1']} (1) vs ${models['2']} (2)`

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
        <hr className="my-4" />
        {/* Link to match */}
        <div className="text-center">
          <a 
            href={`/match/${gameData.metadata.game_id}`}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            view match
          </a>
        </div>
      </div>
  )
}