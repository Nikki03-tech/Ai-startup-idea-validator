import AgentStatus from "../../components/AgentStatus";

export default function ProcessingPage() {
  return (
    <div className="min-h-screen bg-black text-white px-6 py-12">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold mb-4">
          AI Analysis In Progress
        </h1>

        <p className="text-gray-400 mb-10">
          Our AI agents are validating your startup idea...
        </p>

        <div className="space-y-4">
          <AgentStatus name="Web Search Agent" />
          <AgentStatus name="Market Analysis Agent" />
          <AgentStatus name="Competitor Agent" />
          <AgentStatus name="SWOT & Risk Agent" />
          <AgentStatus name="MVP Agent" />
          <AgentStatus name="GTM Strategy Agent" />
          <AgentStatus name="Report Agent" />
        </div>
      </div>
    </div>
  );
}
