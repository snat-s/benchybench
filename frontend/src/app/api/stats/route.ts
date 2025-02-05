import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import path from 'path';

export async function GET() {
  try {
    // Construct the path to the stats file inside completed_games, starting from parent directory
    const statsFilePath = path.join(process.cwd(), '..', 'backend', 'completed_games', 'stats.json');
    
    // Read the entire stats.json file.
    const fileContent = await readFile(statsFilePath, 'utf-8');
    const statsData = JSON.parse(fileContent);

    // For demonstration, we calculate a totalGames count by summing wins, losses, and ties
    // for each player in the stats.
    let totalGames = 0;
    for (const player in statsData) {
      const { wins = 0, losses = 0, ties = 0 } = statsData[player];
      totalGames += wins + losses + ties;
    }

    // Return a default empty object if no data exists
    return NextResponse.json({ 
      totalGames: totalGames, 
      aggregatedData: statsData || {} 
    });

  } catch (error) {
    console.error('Error reading stats:', error);
    // Return a valid JSON response even if there's an error
    return NextResponse.json({ 
      totalGames: 0, 
      aggregatedData: {} 
    });
  }
}