"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function IdeaForm() {
  const router = useRouter();

  const [idea, setIdea] = useState("");
  const [startupName, setStartupName] = useState("");
  const [industry, setIndustry] = useState("");

  const handleSubmit = () => {
    router.push("/processing");
  };

  return (
    <div className="bg-zinc-900 rounded-2xl p-8 border border-zinc-800">
      <div className="space-y-6">
        <input
          type="text"
          placeholder="Startup Name"
          value={startupName}
          onChange={(e) => setStartupName(e.target.value)}
          className="w-full p-4 rounded-xl bg-zinc-800 border border-zinc-700"
        />

        <input
          type="text"
          placeholder="Industry"
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="w-full p-4 rounded-xl bg-zinc-800 border border-zinc-700"
        />

        <textarea
          rows={8}
          placeholder="Describe your startup idea..."
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          className="w-full p-4 rounded-xl bg-zinc-800 border border-zinc-700"
        />

        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 py-4 rounded-xl text-lg font-semibold hover:bg-blue-700"
        >
          Analyze Startup Idea
        </button>
      </div>
    </div>
  );
}
