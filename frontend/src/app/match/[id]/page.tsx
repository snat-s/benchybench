import { notFound } from 'next/navigation'
import GameViewer from '@/components/GameViewer'

interface GameData {
  metadata: {
    game_id: string;
    start_time: string;
    end_time: string;
    models: Record<string, string>;
    game_result: Record<string, string>;
    final_scores: Record<string, number>;
    death_info: Record<string, { reason: string }>;
    max_rounds: number;
    actual_rounds: number;
  };
  rounds: {
    round_number: number;
    move_history?: {
      [modelId: string]: {
        move: string;
        rationale: string;
      };
    }[];
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
}

interface PageProps {
  params: Promise<{
    id: string;
  }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function Page(props: PageProps) {
  const params = await props.params;
  const { id } = params;

  const gamesResponse = await fetch(`${process.env.FLASK_URL}/api/matches/${id}`, { next: { revalidate: 300 } }); // revalidate every 5 minutes

  // If not found or error
  if (!gamesResponse.ok) {
    notFound();
  }

  // Parse the JSON
  const gameData: GameData = await gamesResponse.json();

  return (
    <div className="font-mono max-w-[800px] mx-auto p-5">
      <div className="p-3">
      </div>
      {/* GameViewer is a client component that will show the ASCII board 
          and the logic for Next/Back/Play plus rationales. */}
      <GameViewer gameData={gameData} />
    </div>
  )
}
