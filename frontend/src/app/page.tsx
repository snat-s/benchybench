export const runtime = 'nodejs';

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
    const gamesResponse = await fetch(`${process.env.FLASK_URL}/api/games?limit=16&sort_by=total_score`, { next: { revalidate: 300 } });
    const gamesData = await gamesResponse.json();
    games = gamesData.games;
  } catch (error) {
    console.error("Error fetching games:", error);
    // Optionally set up fallback content
    games = [];
  }

  return (
    <div className="font-mono max-w-[800px] mx-auto pb-5 pr-5 pl-5 pt-3 text-sm">
      <p>
        What happens when you make two LLMs battle head-to-head in snake arena?
        <br />
        We tested 15 LLMs against each other to see who would win.
        <br />
        <br />
        Each snake is randomly initialized. Then we simultaneously ask the two snakes (LLMs) to pick their next move.
        <br />
        The game ends when one snake hits a wall, runs into itself, or runs into the other snake.
        <br />
        <br />
        We then calculate the Elo rating for each snake based on the game results.
        <br />
        <br />
        In general, most interseting matches come from o1, o3, and sonnet. Other LLMs keep hitting the wall.
        <br />
        <br />
        See my thoughts, reflections, and findings <a className="text-blue-500 underline" href="/findings">here</a>.
      </p>
      <hr />
      <br />
      <h2>SnakeBench Rankings:</h2>
      <br />
      <Leaderboard data={leaderboardData} />
      <br />
      <br />
      <h3>Best Matches:</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 pb-4 pt-4">
        {games.map((game: GameData) => (
          <AsciiSnakeGame key={game.metadata.game_id} initialGameData={game} />
        ))}
      </div>
    </div>
  );
}