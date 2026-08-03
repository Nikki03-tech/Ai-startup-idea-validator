"use client";

export default function AgentStatus({
  name,
}: {
  name: string;
}) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex justify-between items-center">
      <span>{name}</span>

      <span className="text-yellow-400 animate-pulse">
        Processing...
      </span>
    </div>
  );
}
