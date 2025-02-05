import { NextResponse } from 'next/server';
import { readdir, readFile } from 'fs/promises';
import path from 'path';

export async function GET(
  request: Request
) {
  try {
    // Get the number of games to return from query params, default to 10
    const { searchParams } = new URL(request.url);
    const limit = Number(searchParams.get('limit')) || 10;

    // Build the directory path for completed games
    const gamesDir = path.join(
      process.cwd(),
      '..',
      'backend',
      'completed_games'
    );

    // Read all files in the directory
    const files = await readdir(gamesDir);
    
    // Filter for snake game files
    const snakeGameFiles = files.filter(
      (file) => file.startsWith('snake_game_') && file.endsWith('.json')
    );

    // Randomly select N game files
    const selectedFiles = snakeGameFiles
      .sort(() => Math.random() - 0.5)
      .slice(0, Math.min(limit, snakeGameFiles.length));

    // Read and parse game data concurrently for each selected file
    const gameDataPromises = selectedFiles.map(async (file) => {
      const filePath = path.join(gamesDir, file);
      try {
        const fileContents = await readFile(filePath, 'utf-8');
        return JSON.parse(fileContents);
      } catch (err) {
        console.error(`Error reading ${filePath}:`, err);
        return null; // handle the error or filter out later
      }
    });
    const games = await Promise.all(gameDataPromises);
    const validGames = games.filter((game) => game !== null);

    // Return the complete game data
    return NextResponse.json({ games: validGames });
  } catch (error) {
    console.error('Error reading game directory:', error);
    return NextResponse.json(
      { error: 'Failed to load game list' },
      { status: 500 }
    );
  }
} 