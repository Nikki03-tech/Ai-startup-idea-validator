import Navbar from "../components/Navbar";
import Hero from "../components/Hero";

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white">
      <Navbar />
      <Hero />

      {/* Features Section */}
      <section className="py-20 px-8">
        <h2 className="text-4xl font-bold text-center mb-12">
          AI Agents
        </h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[
            "Web Search Agent",
            "Market Analysis",
            "Competitor Analysis",
            "SWOT Analysis",
            "MVP Recommendation",
            "GTM Strategy",
          ].map((item) => (
            <div
              key={item}
              className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 hover:border-blue-500 transition"
            >
              <h3 className="text-xl font-semibold">{item}</h3>
              <p className="text-gray-400 mt-3">
                AI-powered insights to validate startup ideas.
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Workflow Section */}
      <section className="py-20 px-8 bg-zinc-950">
        <h2 className="text-4xl font-bold text-center mb-12">
          How It Works
        </h2>

        <div className="max-w-4xl mx-auto flex flex-col items-center gap-6 text-xl">
          <div>1️⃣ Submit Startup Idea</div>
          <div>⬇️</div>

          <div>2️⃣ AI Agents Analyze</div>
          <div>⬇️</div>

          <div>3️⃣ Generate Validation Report</div>
          <div>⬇️</div>

          <div>4️⃣ Chat with AI Advisor</div>
        </div>
      </section>
    </main>
  );
}
