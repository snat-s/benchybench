import Link from 'next/link'

type LeaderboardItem = {
  rank: number;
  model: string;
  elo: number;
  wins: number;
  losses: number;
  ties: number;
  apples: number;
  link: string;
};

interface LeaderboardProps {
  data: LeaderboardItem[];
}

export default function Leaderboard({ data }: LeaderboardProps) {
  return (
    <div style={{ maxHeight: '400px', overflowY: 'auto', overflowX: 'hidden', padding: '0.5em' }}>
      <pre style={{ fontSize: '1em', margin: 0 }}>
        {`Rank | Model                               | ELO  | Wins | Losses | Ties | Apples | View
-----+-------------------------------------+------+------+--------+------+--------+------`}
      </pre>
      <div style={{ fontSize: '1em', fontFamily: 'monospace', whiteSpace: 'pre' }}>
        {data.map((player) => (
          <div key={player.model}>
            {player.rank.toString().padStart(4)} |{' '}
            {player.model.padEnd(35)} |{' '}
            {Math.round(player.elo).toString().slice(0, 4).padStart(4)} |{' '}
            {player.wins.toString().padStart(4)} |{' '}
            {player.losses.toString().padStart(6)} |{' '}
            {player.ties.toString().padStart(4)} |{' '}
            {player.apples.toString().padStart(6)} |{' '}
            <Link href={player.link} style={{ textDecoration: 'underline' }}>
              -&gt;
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
