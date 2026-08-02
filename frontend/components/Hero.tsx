import Link from "next/link";

export default function Hero() {
  return (
    <section className="flex flex-col items-center justify-center text-center py-32 px-6">
      <h1 className="text-6xl font-bold max-w-5xl">
        Validate Your Startup Idea
        <span className="text-blue-500"> Before You Build It</span>
      </h1>

      <p className="mt-8 text-xl text-gray-400 max-w-3xl">
        AI-powered market research, competitor analysis, SWOT analysis,
        MVP recommendations, and go-to-market strategy generation.
      </p>

      <Link href="/submit">
        <button className="mt-10 bg-blue-600 px-8 py-4 rounded-xl text-lg hover:bg-blue-700 transition">
          Analyze Idea →
        </button>
      </Link>
    </section>
  );
}
