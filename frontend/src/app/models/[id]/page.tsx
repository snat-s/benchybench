import AnimatedTitle from '@/components/AnimatedTitle'

interface Game {
  game_id: string;
  my_score: number;
  opponent_score: number;
  opponent_model: string;
  start_time: string;
  end_time: string;
  result: string;
  death_info?: {
    reason: string;
    round: number;
  };
}

interface ModelStats {
  wins: number;
  losses: number;
  ties: number;
  apples_eaten: number;
  elo: number;
  games: Game[];
}

export default async function ModelGamesPage({ params }: { params: Promise<{ id: string }> }) {
  // Await the params object
  const { id: modelId } = await params;
  
  // Fetch the full stats
  const baseUrl = process.env.BASE_URL || `https://${process.env.VERCEL_URL}`;
  const response = await fetch(`${baseUrl}/api/stats`, { next: { revalidate: 300 } });
  const stats = await response.json();

  // Use the awaited modelId
  const modelStats: ModelStats = stats['aggregatedData'][modelId];

  if (!modelStats) {
    return (
      <div style={{ fontFamily: "monospace", maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
        <AnimatedTitle />
        <hr />
        <p>Model &quot;{modelId}&quot; not found.</p>
      </div>
    );
  }

  const games = modelStats.games || [];

  return (
    <div style={{ fontFamily: "monospace", maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
      <AnimatedTitle />
      <h1 className="text-xl font-bold mb-4 pt-4">Game Records for Model: {modelId}</h1>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Opponent</th>
            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Start Time</th>
            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Duration</th>
            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Outcome</th>
            <th style={{ border: "1px solid #ddd", padding: "8px" }}>Loss Reason</th>
            <th style={{ border: "1px solid #ddd", padding: "8px", textDecoration: "underline" }}>View Match</th>
          </tr>
        </thead>
        <tbody>
          {games.map((game, index) => {
            // For a lost game, show the loss reason (if available)
            const lossReason = game.result === "lost" && game.death_info ? game.death_info.reason : "";
            
            // Determine the background color for the outcome
            const outcomeBackground =
              game.result === "lost" ? "#ffebee" : game.result === "won" ? "#e8f5e9" : "inherit";
            
            return (
              <tr key={game.game_id || index}>
                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{game.opponent_model}</td>
                <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                  {new Date(game.start_time).toLocaleString('en-US', {
                    year: 'numeric',
                    month: '2-digit', 
                    day: '2-digit',
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                  }).replace(',','')}
                </td>
                <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                  {(() => {
                    const start = new Date(game.start_time);
                    const end = new Date(game.end_time);
                    const diffMs = end.getTime() - start.getTime();
                    const minutes = Math.floor(diffMs / 60000);
                    const seconds = Math.floor((diffMs % 60000) / 1000);
                    return `${minutes}min ${seconds}sec`;
                  })()}
                </td>
                <td style={{ border: "1px solid #ddd", padding: "8px", backgroundColor: outcomeBackground }}>
                  {game.result}
                </td>
                <td style={{ border: "1px solid #ddd", padding: "8px" }}>{lossReason}</td>
                <td style={{ border: "1px solid #ddd", padding: "8px" }}>
                  <a href={`/match/${game.game_id}`}>View Match</a>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <hr />
      <p style={{ textAlign: "center", fontSize: "0.8em" }}>
        Last updated: {new Date().toLocaleString()}
      </p>
    </div>
  );
}

