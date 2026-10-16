"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type State = "checking" | "ok" | "down";

export default function ApiStatus() {
  const [state, setState] = useState<State>("checking");

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_URL}/health`)
      .then((r) => r.json())
      .then((d) => !cancelled && setState(d.status === "ok" ? "ok" : "down"))
      .catch(() => !cancelled && setState("down"));
    return () => {
      cancelled = true;
    };
  }, []);

  const styles: Record<State, string> = {
    checking: "bg-slate-400",
    ok: "bg-verified",
    down: "bg-danger",
  };
  const label: Record<State, string> = {
    checking: "Checking API…",
    ok: "API online",
    down: "API unreachable",
  };

  return (
    <span id="api-status" className="flex items-center gap-2 text-sm text-slate-400">
      <span className={`pulse-dot h-2 w-2 rounded-full ${styles[state]}`} />
      {label[state]}
    </span>
  );
}
