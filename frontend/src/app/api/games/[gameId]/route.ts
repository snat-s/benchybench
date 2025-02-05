import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import path from 'path';

export async function GET(
  request: Request,
  { params }: { params: { gameId: string } }
) {
  try {
    // Build the path using the game id from the URL.
    const gameFilePath = path.join(
      process.cwd(),
      '..',
      'backend',
      'completed_games',
      `snake_game_${params.gameId}.json`
    );

    // Read and parse the JSON file.
    const fileContent = await readFile(gameFilePath, 'utf-8');
    const gameData = JSON.parse(fileContent);

    // Return the game data directly.
    return NextResponse.json(gameData);
  } catch (error) {
    console.error(`Error reading game data for game id ${params.gameId}:`, error);
    // Return an error response if anything goes wrong.
    return NextResponse.json(
      { error: 'Failed to load game data' },
      { status: 500 }
    );
  }
} 