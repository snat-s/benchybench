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
    <>
      <pre style={{ fontSize: '1em' }}>
        {`Rank | Model                       | ELO  | Wins | Losses | Ties | Apples | View
-----+-----------------------------+------+------+--------+------+--------+------`}
      </pre>
      <div style={{ fontSize: '1em', fontFamily: "monospace", whiteSpace: "pre" }}>
        {data.map((player) => (
          <div key={player.model}>
            {player.rank.toString().padStart(4)} |{' '}
            {player.model.padEnd(27)} |{' '}
            {Math.round(player.elo).toString().slice(0, 4).padStart(4)} |{' '}
            {player.wins.toString().padStart(4)} |{' '}
            {player.losses.toString().padStart(6)} |{' '}
            {player.ties.toString().padStart(4)} |{' '}
            {player.apples.toString().padStart(6)} |{' '}
            <Link href={player.link} style={{ textDecoration: "underline" }}>
              -&gt;
            </Link>
          </div>
        ))}
      </div>
    </>
  )
}
