export default function Navbar() {
  return (
    <nav className="flex justify-between items-center px-8 py-5 border-b border-zinc-800">
      <h1 className="text-2xl font-bold text-blue-500">
        Startup Validator AI
      </h1>

      <button className="bg-blue-600 px-5 py-2 rounded-lg hover:bg-blue-700">
        Get Started
      </button>
    </nav>
  );
}
