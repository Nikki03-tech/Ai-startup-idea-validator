import IdeaForm from "../../components/IdeaForm";

export default function SubmitPage() {
  return (
    <div className="min-h-screen bg-black text-white px-6 py-12">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold mb-4">
          Submit Your Startup Idea
        </h1>

        <p className="text-gray-400 mb-10">
          Describe your startup idea and let our AI agents validate it.
        </p>

        <IdeaForm />
      </div>
    </div>
  );
}
