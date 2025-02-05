import AnimatedTitle from '@/components/AnimatedTitle'
import { notFound } from 'next/navigation'
import GameViewer from '@/components/GameViewer'

interface GameData {
  // Adjust this interface to match your exact JSON structure
  metadata: {
    game_id: string;
    start_time: string;
    end_time: string;
    models: Record<string, string>;
    game_result: Record<string, string>;
    final_scores: Record<string, number>;
    death_info: any;
    max_rounds: number;
    actual_rounds: number;
  };
  rounds: Array<any>;
}

export default async function Page({ params }: { params: { id: string } }) {
  const { id } = params;

  const gamesResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/games/${id}`, { next: { revalidate: 300 } }); // revalidate every 5 minutes

  // If not found or error
  if (!gamesResponse.ok) {
    notFound();
  }

  // Parse the JSON
  const gameData: GameData = await gamesResponse.json();

  // Grab model names for the title if needed
  const modelOne = gameData.metadata.models['1'];
  const modelTwo = gameData.metadata.models['2'];

  return (
    <div style={{ fontFamily: "monospace", maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
      <AnimatedTitle />
      {/* Title of the match */}
      {/* <h2>{modelOne} vs. {modelTwo}</h2> */}
      
      {/* GameViewer is a client component that will show the ASCII board 
          and the logic for Next/Back/Play plus rationales. */}
      <GameViewer gameData={gameData} />
    </div>
  )
}
