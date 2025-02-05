import statsData from '@/data/stats.json';
import { NextResponse } from 'next/server';

interface StatsEntry {
  wins: number;
  losses: number;
  ties: number;
  apples_eaten: number;
  elo: number;
  games: Array<{
    game_id: string;
    my_score: number;
    opponent_score: number;
    opponent_model: string;
    result: string;
    death_info: Record<string, unknown>;
  }>;
}

type StatsData = Record<string, StatsEntry>;

export async function GET() {
  try {
    let totalGames = 0;
    for (const player in statsData as StatsData) {
      const { wins = 0, losses = 0, ties = 0 } = (statsData as StatsData)[player];
      totalGames += wins + losses + ties;
    }

    return NextResponse.json({ 
      totalGames: totalGames, 
      aggregatedData: statsData || {} 
    });

  } catch (error) {
    console.error('Error processing stats:', error);
    return NextResponse.json({ 
      totalGames: 0, 
      aggregatedData: {} 
    });
  }
}