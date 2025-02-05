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

    // Build the directory path for completed games (updated to new location)
    const gamesDir = path.join(process.cwd(), 'src', 'data', 'completed_games');

    // Read all files in the directory
    const files = await readdir(gamesDir);
    
    // Filter for snake game files
    const snakeGameFiles = files.filter(
      (file) => file.startsWith('snake_game_') && file.endsWith('.json')
    );

    // Randomly shuffle and then select up to `limit` game files
    const selectedFiles = snakeGameFiles.sort(() => Math.random() - 0.5).slice(0, Math.min(limit, snakeGameFiles.length));

    // Read and parse each selected JSON file concurrently
    const gameDataPromises = selectedFiles.map(async (file) => {
      const filePath = path.join(gamesDir, file);
      try {
        const fileContents = await readFile(filePath, 'utf-8');
        return JSON.parse(fileContents);
      } catch (error) {
        console.error(`Error reading or parsing ${filePath}:`, error);
        return null;
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