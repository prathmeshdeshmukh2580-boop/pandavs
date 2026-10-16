import ApiStatus from "@/components/ApiStatus";

const STAGES = ["Planner", "Generator", "Verifier", "Renderer"];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center px-6 py-16">
      <div className="mb-6 flex items-center justify-between">
        <span className="rounded-full border border-verified/30 bg-verified/10 px-3 py-1 text-xs font-medium tracking-wide text-verified">
          PROTOTYPE · PHASE 0
        </span>
        <ApiStatus />
      </div>

      <h1 className="bg-gradient-to-br from-white via-indigo-200 to-emerald-300 bg-clip-text text-5xl font-semibold leading-tight tracking-tight text-transparent sm:text-6xl">
        Verified Course Material Studio
      </h1>
      <p className="mt-5 max-w-2xl text-lg text-slate-400">
        Training decks where every code snippet is compiled and run in a sandbox before it reaches you.
        Nothing ships unverified.
      </p>

      <ol className="glass mt-12 grid grid-cols-2 gap-px overflow-hidden sm:grid-cols-4" aria-label="Pipeline">
        {STAGES.map((stage, i) => (
          <li key={stage} className="bg-ink-900/60 p-5 transition-colors hover:bg-ink-800/80">
            <span className="font-mono text-xs text-slate-500">0{i + 1}</span>
            <p className="mt-1 font-medium text-slate-100">{stage}</p>
          </li>
        ))}
      </ol>
    </main>
  );
}
