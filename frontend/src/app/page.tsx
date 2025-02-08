export const runtime = 'nodejs';

import AnimatedTitle from '@/components/AnimatedTitle'
import AsciiSnakeGame from '@/components/AsciiSnakePlayer';
import Leaderboard from '@/components/Leaderboard'

// Add these type definitions at the top of the file
type StatsData = {
  elo: number;
  wins: number;
  losses: number;
  ties: number;
  apples_eaten: number;
};

type GameData = {
  metadata: {
    game_id: string;
    models: { [key: string]: string };
    game_result: { [key: string]: string };
    final_scores: { [key: string]: number };
  };
  rounds: {
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
  }[];
};

export default async function Page() {
  let aggregatedData: Record<string, StatsData> = {};
  try {
    const response = await fetch(`${process.env.FLASK_URL}/api/stats`, { next: { revalidate: 300 } });
    const data = await response.json();
    aggregatedData = data.aggregatedData;
  } catch (error) {
    console.error("Error fetching stats:", error);
    // Optionally set up fallback data
    aggregatedData = {};
  }

  // Transform the stats data into the leaderboard format
  const leaderboardData = Object.entries(aggregatedData as Record<string, StatsData>)
    .map(([model, data], index) => ({
      rank: index + 1,
      model: model,
      elo: data.elo || 1000,
      wins: data.wins || 0,
      losses: data.losses || 0,
      ties: data.ties || 0,
      apples: data.apples_eaten || 0,
      link: `/models/${model}`
    }))
    .sort((a, b) => b.elo - a.elo)
    .map((item, index) => ({ ...item, rank: index + 1 }));

  let games: GameData[] = [];
  try {
    const gamesResponse = await fetch(`${process.env.FLASK_URL}/api/games?limit=16`, { next: { revalidate: 300 } });
    const gamesData = await gamesResponse.json();
    games = gamesData.games;
  } catch (error) {
    console.error("Error fetching games:", error);
    // Optionally set up fallback content
    games = [];
  }

  return (
    <div style={{ fontFamily: "monospace", maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
      <AnimatedTitle />
      <hr />
      <p>
        What happens when you make two LLMs fight in snake arena?
        <br />
        We tested 12 LLMs against each other to see who would win.
      </p>
      <hr />
      <br />
      <h2>SnakeBench Rankings:</h2>
      <br />
      <Leaderboard data={leaderboardData} />
      <br />
      <br />
      <h3>Latest Matches:</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 pb-4 pt-4">
        {games.map((game: GameData) => (
          <AsciiSnakeGame key={game.metadata.game_id} initialGameData={game} />
        ))}
      </div>
      <p>
        Made with ❤️ by <a href="https://www.x.com/gregkamradt">Greg Kamradt</a> - <a href="https://github.com/gkamradt/SnakeBench">Code Open Source</a>
      </p>
      <p style={{ textAlign: "center", fontSize: "0.8em" }}>
        Last updated: February 5, 2025 8:27 AM PT
      </p>
    </div>
  );
}