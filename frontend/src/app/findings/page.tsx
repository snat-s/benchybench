export const runtime = 'nodejs';

export default function FindingsPage() {
  return (
    <div className="font-mono max-w-[800px] mx-auto p-5 text-sm">
      <hr />
      <h1 className="text-xl font-bold mb-4">Findings & Reflections</h1>
      <section className="mb-6">
        <h2 className="text-lg font-bold mb-2">Key Observations</h2>
        <p>
          • Google models experienced unexpected rate limits despite being on a paid tier, resulting in fewer results and prompting a deeper dive into GCP settings.
          <br /><br />
          • Many LLMs misinterpreted the board layout provided in text format. This led to cases where models incorrectly believed where their snake&apos;s head was or even ran backwards into their own tail.
          <br /><br />
          • Lower-tier models (including GPT-3.5 Turbo and Haiku) struggled significantly, while GPT-4, Gemini 2.0, and especially o3 Mini (which showcased more reflective thinking) performed noticeably better.
          <br /><br />
          • Each LLM took turns simutaniously. The turn-based mechanics highlighted internal chain-of-thought processes. I saved the model responses for analysis.
        </p>
      </section>

      <hr />

      <section className="mb-6">
        <h2 className="text-lg font-bold mb-2">Methodology</h2>
        <p>
          • The board was provided in a textual format. This required us to be explicit about the XY coordinate system—ensuring models understood directional moves—because without a true 2D representation, spatial reasoning was often lost in translation.
        </p>
      </section>

      <hr />

      <section className="mb-6">
        <h2 className="text-lg font-bold mb-2">Detailed Analysis</h2>
        <p>
          • The text-based board representation proved challenging for LLMs. Since the board is treated as tokens rather than a true 2D map, models often misjudged positions and made erroneous moves, such as running into walls or colliding with themselves.
          <br /><br />
          • While one idea was to restrict models to only legal moves to prevent such errors, doing so might narrow their strategic playing field, effectively handicapping their natural decision-making.
          <br /><br />
          • The study underscored that even with explicit positional guidance, a purely token-based interpretation has inherent limitations when simulating spatial dynamics.
        </p>
      </section>

      <hr />

      <section className="mb-6">
        <h2 className="text-lg font-bold mb-2">Future Work</h2>
        <p>
          • With better models, use bigger board sizes.
          <br /><br />
          • Add more snakes, more apples, and add walls to the game.
        </p>
      </section>
      <section className="mb-6">
        <h2 className="text-lg font-bold mb-2">Prompt Example</h2>
        <p>
        You are controlling a snake in a multi-apple Snake game.The board size is 10x10. Normal X,Y coordinates are used. Coordinates range from (0,0) at bottom left to (9,9) at top right.
        <br /><br />
        Apples at: (9, 6), (0, 2), (5, 9), (1, 7), (9, 7)
        <br /><br />
        Your snake ID: 1 which is currently positioned at (5, 1)
        <br /><br />
        Enemy snakes positions:
        * Snake #2 is at position (7, 1) with body at []
        <br /><br />
        Board state:
        <br /><br />
        9 . . . . . A . . . .
        <br />
        8 . . . . . . . . . .
        <br />
        7 . A . . . . . . . A
        <br />
        6 . . . . . . . . . A
        <br />
        5 . . . . . . . . . .
        <br />
        4 . . . . . . . . . .
        <br />
        3 . . . . . . . . . .
        <br />
        2 A . . . . . . . . .
        <br />
        1 . . . . . 1 . 2 . .
        <br />
        0 . . . . . . . . . .
        <br />
        0 1 2 3 4 5 6 7 8 9
        <br /><br />
        --Your last move information:--
        <br /><br />
        Direction: LEFT
        <br /><br />
        Rationale: I’m noticing that (0,2) is the closest apple from our head at (6,1) (it’s 7 steps away by Manhattan distance), and it’s away from the enemy snake at (7,0). Right now our immediate options are:
        <br /><br />
        • UP → goes to (6,2)
        <br />
        • RIGHT → goes to (7,1) (closer to the enemy snake&apos;s territory)
        <br />
        • LEFT → goes to (5,1)
        <br />
        • DOWN → goes to (6,0)
        <br /><br />
        Moving RIGHT or DOWN brings us closer to the enemy snake at (7,0) or even out of safe bounds. Moving UP would work, but LEFT starts guiding us toward (0,2). Thus, I decide to move LEFT.
        <br /><br />
        Strategy for future turns: I’ll aim to continue left and then maneuver upward to reach the apple at (0,2) while remaining mindful of potential enemy moves.
        <br /><br />
        My decided next move: LEFT.
        <br /><br />
        --End of your last move information.--
        <br /><br />
        Rules:
        1) If you move onto an apple, you grow and gain 1 point.
        2) If you run into a wall (outside the range of the listed coordinates), another snake, or yourself (like go backwards), you die.
        3) The goal is to have the most points by the end.
        <br /><br />
        Decreasing your x coordinate is to the left, increasing your x coordinate is to the right.
        <br /><br />
        Decreasing your y coordinate is down, increasing your y coordinate is up.
        <br /><br />
        You may think out loud first then respond with the direction.
        <br /><br />
        You may also state a strategy you want to tell yourself next turn.
        <br /><br />
        End your response with your decided next move: UP, DOWN, LEFT, or RIGHT.
        </p>
      </section>
    </div>
  );
}
