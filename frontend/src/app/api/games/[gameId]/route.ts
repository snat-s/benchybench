import { NextRequest, NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ gameId: string }> }
) {
  try {
    // Need to await params since it's now a Promise
    const gameId = (await params).gameId;
    
    const gameFilePath = path.join(
      process.cwd(),
      '..',
      'backend',
      'completed_games',
      `snake_game_${gameId}.json`
    );

    // Read and parse the JSON file.
    const fileContent = await readFile(gameFilePath, 'utf-8');
    const gameData = JSON.parse(fileContent);

    // Return the game data directly.
    return NextResponse.json(gameData);
  } catch (error) {
    console.error(`Error reading game data for game id ${(await params).gameId}:`, error);

    return NextResponse.json(
      { error: 'Failed to load game data' },
      { status: 500 }
    );
  }
}
