"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  RotateCw,
  RotateCcw,
  PlusCircle,
  X,
  Download,
  FileCheck2,
  Cpu,
  Layers,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Code2,
  Sparkles,
  BookOpen,
  Terminal,
  ExternalLink,
  CheckCircle2,
  XCircle,
  Clock,
  Zap,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function StudioDashboard() {
  // Generation Form State
  const [topic, setTopic] = useState("Spring Boot 3 REST APIs & Architecture");
  const [level, setLevel] = useState("beginner");
  const [minutes, setMinutes] = useState(90);
  const [stackType, setStackType] = useState<"java" | "python">("java");

  // Pipeline Execution State
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStage, setCurrentStage] = useState<string | null>(null);
  const [stageProgress, setStageProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [activeDeckId, setActiveDeckId] = useState<string>("d_001");

  // Loaded Deck & Slide Navigation
  const [deck, setDeck] = useState<any>(null);
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);
  const [report, setReport] = useState<any>(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeDiff, setUpgradeDiff] = useState<any>(null);

  // Self-Healing Theater State
  const [showTheaterModal, setShowTheaterModal] = useState(false);
  const [theaterExample, setTheaterExample] = useState<"python_add" | "python_boundary" | "python_syntax">("python_add");
  const [theaterRunId, setTheaterRunId] = useState<string | null>(null);
  const [theaterRunning, setTheaterRunning] = useState(false);
  const [theaterStage, setTheaterStage] = useState<string>("idle");
  const [theaterProgress, setTheaterProgress] = useState(0);
  const [theaterLogs, setTheaterLogs] = useState<string[]>([
    "[Theater Ready] Click 'Watch AI Fix Its Own Code' to launch real execution pipeline."
  ]);
  const [theaterRepairedCode, setTheaterRepairedCode] = useState<string>("");
  const [theaterVerifiedStatus, setTheaterVerifiedStatus] = useState<"idle" | "verifying" | "passed" | "failed">("idle");
  const [theaterMeta, setTheaterMeta] = useState<any>(null);
  const [isAddingToDeck, setIsAddingToDeck] = useState(false);

  const THEATER_PRESETS = {
    python_add: {
      name: "Arithmetic Operator Bug",
      code: `def add(a: int, b: int) -> int:\n    """Adds two integers and returns their sum."""\n    return a - b`
    },
    python_boundary: {
      name: "Off-by-One Loop Boundary Bug",
      code: `def sum_to_n(n: int) -> int:\n    """Calculates the sum of integers from 1 up to and including n."""\n    total = 0\n    for i in range(1, n):\n        total += i\n    return total`
    },
    python_syntax: {
      name: "Missing Colon Syntax Error",
      code: `def greet(name: str) -> str\n    return f"Hello, {name}!"`
    }
  };

  const startTheaterDemo = async () => {
    setTheaterRunning(true);
    setTheaterStage("initializing");
    setTheaterProgress(10);
    setTheaterVerifiedStatus("verifying");
    setTheaterRepairedCode("");
    setTheaterMeta(null);
    setTheaterLogs([`[Initiating] Starting controlled failure demo: ${theaterExample}...`]);

    try {
      const resp = await fetch(`${API_BASE}/api/self-heal/demo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ example_id: theaterExample }),
      });
      if (!resp.ok) throw new Error("Failed to start self-healing run");
      const { run_id } = await resp.json();
      setTheaterRunId(run_id);

      const sse = new EventSource(`${API_BASE}/api/self-heal/${run_id}/events`);
      sse.onmessage = (event) => {
        try {
          const ev = JSON.parse(event.data);
          setTheaterProgress(ev.progress);
          setTheaterStage(ev.stage);
          setTheaterLogs((prev) => [...prev, `[${ev.stage.toUpperCase()}] ${ev.message}`]);

          if (ev.meta && ev.meta.repaired_code) {
            setTheaterRepairedCode(ev.meta.repaired_code);
          }
          if (ev.stage === "verification_passed") {
            setTheaterVerifiedStatus("passed");
            setTheaterMeta(ev.meta);
          } else if (ev.stage === "verification_failed_final") {
            setTheaterVerifiedStatus("failed");
          } else if (ev.stage === "complete") {
            sse.close();
            setTheaterRunning(false);
          }
        } catch (e) {
          console.error(e);
        }
      };
      sse.onerror = () => {
        sse.close();
        setTheaterRunning(false);
      };
    } catch (err: any) {
      setTheaterRunning(false);
      setTheaterLogs((prev) => [...prev, `[ERROR] ${err.message}`]);
    }
  };

  const addTheaterToDeck = async () => {
    if (!theaterRunId || theaterVerifiedStatus !== "passed") return;
    setIsAddingToDeck(true);
    try {
      const targetDeck = deck ? deck.deck_id : "d_001";
      const resp = await fetch(`${API_BASE}/api/self-heal/${theaterRunId}/add-to-deck`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ deck_id: targetDeck }),
      });
      if (!resp.ok) throw new Error("Could not add to deck");
      const data = await resp.json();
      await loadDeck(data.deck_id);
      alert(`Success! Verified slide "${data.slide_title}" added to deck.`);
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    } finally {
      setIsAddingToDeck(false);
    }
  };


  // Load initial demo deck
  useEffect(() => {
    loadDeck("d_001");
  }, []);

  const loadDeck = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/decks/${id}`);
      if (res.ok) {
        const data = await res.json();
        setDeck(data);
        setActiveDeckId(id);
        setActiveSlideIndex(0);
        // Also fetch report
        const repRes = await fetch(`${API_BASE}/decks/${id}/report`);
        if (repRes.ok) {
          const repData = await repRes.json();
          setReport(repData);
        }
      }
    } catch (e) {
      console.error("Failed to load deck:", e);
    }
  };

  const startGeneration = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setCurrentStage("planner");
    setStageProgress(10);
    setStatusMessage("Submitting generation request to orchestrator...");

    const stack =
      stackType === "java"
        ? { java: "21", spring_boot: "3.3" }
        : { python: "3.12", framework: "fastapi" };

    try {
      const resp = await fetch(`${API_BASE}/decks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, level, minutes: Number(minutes), stack }),
      });

      if (!resp.ok) throw new Error("Generation request failed");
      const { deck_id } = await resp.json();
      setActiveDeckId(deck_id);

      // Connect to SSE stream
      const eventSource = new EventSource(`${API_BASE}/decks/${deck_id}/events`);
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setCurrentStage(data.stage);
          setStageProgress(data.progress || 0);
          setStatusMessage(data.message || "");

          if (data.stage === "complete") {
            eventSource.close();
            setIsGenerating(false);
            loadDeck(deck_id);
          } else if (data.stage === "failed") {
            eventSource.close();
            setIsGenerating(false);
            alert(`Generation failed: ${data.message}`);
          }
        } catch (err) {
          console.error("Error parsing SSE:", err);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsGenerating(false);
        loadDeck(deck_id);
      };
    } catch (err: any) {
      setIsGenerating(false);
      alert(err.message || "Failed to start generation");
    }
  };

  const regenerateCurrentSlide = async () => {
    if (!deck || !deck.slides[activeSlideIndex]) return;
    const slideId = deck.slides[activeSlideIndex].id;
    try {
      const resp = await fetch(
        `${API_BASE}/decks/${deck.deck_id}/slides/${slideId}/regenerate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt_hint: "Add deeper error handling & constraints" }),
        }
      );
      if (resp.ok) {
        const data = await resp.json();
        const updatedSlides = [...deck.slides];
        updatedSlides[activeSlideIndex] = data.slide;
        setDeck({ ...deck, slides: updatedSlides });
        alert(`Slide ${slideId} regenerated and re-verified successfully!`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpgrade = async () => {
    if (!deck) return;
    try {
      const targetStack =
        stackType === "java"
          ? { java: "21", spring_boot: "3.3" }
          : { python: "3.12", framework: "fastapi" };

      const resp = await fetch(`${API_BASE}/decks/${deck.deck_id}/upgrade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_stack: targetStack }),
      });
      if (resp.ok) {
        const diffData = await resp.json();
        setUpgradeDiff(diffData);
        loadDeck(deck.deck_id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const activeSlide = deck?.slides?.[activeSlideIndex];

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg text-white shadow-lg shadow-indigo-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white">
                Verified Course Material Studio
              </h1>
              <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-medium">
                Zero-Trust Pipeline
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Only verified content reaches the presentation deck
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowTheaterModal(true)}
            className="text-xs bg-gradient-to-r from-purple-600 via-indigo-600 to-emerald-500 hover:from-purple-500 hover:to-emerald-400 text-white font-semibold px-3.5 py-1.5 rounded-md flex items-center gap-1.5 shadow-lg shadow-indigo-500/25 transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Watch AI Fix Its Own Code</span>
          </button>
          <button
            onClick={() => loadDeck("d_001")}
            className="text-xs border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-md flex items-center gap-1.5 transition"
          >
            <BookOpen className="w-3.5 h-3.5" />
            Load Sample Deck (d_001)
          </button>
          {deck && (
            <>
              <button
                onClick={() => setShowReportModal(true)}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 px-3 py-1.5 rounded-md flex items-center gap-1.5 transition"
              >
                <FileCheck2 className="w-3.5 h-3.5" />
                Audit Report
              </button>
              <a
                href={`${API_BASE}/decks/${deck.deck_id}/export?format=pptx`}
                download
                className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3.5 py-1.5 rounded-md flex items-center gap-1.5 shadow-md transition"
              >
                <Download className="w-3.5 h-3.5" />
                Export .PPTX
              </a>
            </>
          )}
        </div>
      </header>

      {/* Main Workspace Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 max-w-[1600px] mx-auto w-full">
        {/* Left Column: Generator Configuration & Pipeline Monitor (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          {/* AI Code Verification & Self-Healing Theater Card */}
          <div className="bg-gradient-to-br from-indigo-950/70 via-slate-900 to-purple-950/50 border border-indigo-500/40 rounded-xl p-5 shadow-lg space-y-3 relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                </span>
                <div>
                  <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
                    AI Code Verification & Self-Healing
                    <span className="text-[9px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-1.5 py-0.5 rounded font-semibold uppercase">
                      Live Theater
                    </span>
                  </h2>
                  <p className="text-[11px] text-slate-400">
                    Watch Pandavs detect, repair, and re-verify faulty code automatically.
                  </p>
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowTheaterModal(true)}
              className="w-full bg-gradient-to-r from-indigo-600 via-purple-600 to-emerald-600 hover:from-indigo-500 hover:to-emerald-500 text-white font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/30 transition text-xs"
            >
              <Play className="w-3.5 h-3.5 text-white" />
              <span>Watch AI Fix Its Own Code</span>
            </button>
          </div>

          {/* Generation Form Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
                Course Generator
              </h2>
            </div>

            <form onSubmit={startGeneration} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Topic / Title
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Audience Level
                  </label>
                  <select
                    value={level}
                    onChange={(e) => setLevel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Duration (Minutes)
                  </label>
                  <input
                    type="number"
                    value={minutes}
                    onChange={(e) => setMinutes(Number(e.target.value))}
                    min={15}
                    max={240}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Target Architecture Stack
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setStackType("java")}
                    className={`py-2 px-3 text-xs rounded-lg border text-left flex flex-col gap-0.5 transition ${
                      stackType === "java"
                        ? "border-indigo-500 bg-indigo-500/10 text-white font-medium"
                        : "border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <span className="font-semibold">Java 21</span>
                    <span className="text-[10px] text-slate-400">Spring Boot 3.3</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setStackType("python")}
                    className={`py-2 px-3 text-xs rounded-lg border text-left flex flex-col gap-0.5 transition ${
                      stackType === "python"
                        ? "border-indigo-500 bg-indigo-500/10 text-white font-medium"
                        : "border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    <span className="font-semibold">Python 3.12</span>
                    <span className="text-[10px] text-slate-400">FastAPI & AsyncIO</span>
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isGenerating}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 transition text-sm"
              >
                {isGenerating ? (
                  <>
                    <RotateCw className="w-4 h-4 animate-spin" />
                    Executing Pipeline...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Generate Verified Deck
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Pipeline Live Progress Card */}
          {(isGenerating || currentStage) && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-semibold tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                  Live Verification Core
                </span>
                <span className="text-xs font-bold text-indigo-400">{stageProgress}%</span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full transition-all duration-300"
                  style={{ width: `${stageProgress}%` }}
                />
              </div>

              {/* Stage Pills */}
              <div className="grid grid-cols-4 gap-1 text-[11px] text-center">
                <div
                  className={`py-1 rounded ${
                    currentStage === "planner"
                      ? "bg-indigo-500 text-white font-semibold"
                      : "bg-slate-950 text-slate-400"
                  }`}
                >
                  Planner
                </div>
                <div
                  className={`py-1 rounded ${
                    currentStage === "generator"
                      ? "bg-indigo-500 text-white font-semibold"
                      : "bg-slate-950 text-slate-400"
                  }`}
                >
                  Generator
                </div>
                <div
                  className={`py-1 rounded ${
                    currentStage === "verifier"
                      ? "bg-emerald-600 text-white font-semibold animate-pulse"
                      : "bg-slate-950 text-slate-400"
                  }`}
                >
                  Verifier
                </div>
                <div
                  className={`py-1 rounded ${
                    currentStage === "renderer" || currentStage === "complete"
                      ? "bg-indigo-500 text-white font-semibold"
                      : "bg-slate-950 text-slate-400"
                  }`}
                >
                  Renderer
                </div>
              </div>

              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 flex items-start gap-2">
                <Terminal className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{statusMessage || "Pipeline ready."}</span>
              </div>
            </div>
          )}

          {/* Slide List Navigator */}
          {deck && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm flex flex-col flex-1">
              <div className="flex items-center justify-between mb-3 px-1">
                <span className="text-xs uppercase font-semibold tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5" />
                  Slides ({deck.slides.length})
                </span>
                <span className="text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  100% Verified
                </span>
              </div>

              <div className="space-y-1.5 overflow-y-auto max-h-[360px] pr-1">
                {deck.slides.map((s: any, idx: number) => {
                  const hasCode = s.code && s.code.length > 0;
                  const isVerified = hasCode ? s.code[0].verified === "passed" : true;
                  const isActive = idx === activeSlideIndex;

                  return (
                    <button
                      key={s.id}
                      onClick={() => setActiveSlideIndex(idx)}
                      className={`w-full text-left p-2.5 rounded-lg border text-xs flex items-center justify-between transition ${
                        isActive
                          ? "border-indigo-500 bg-indigo-500/10 text-white font-medium"
                          : "border-slate-800/80 bg-slate-950/60 hover:bg-slate-800/50 text-slate-300"
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate">
                        <span className="text-slate-500 font-mono text-[10px]">
                          {idx + 1 < 10 ? `0${idx + 1}` : idx + 1}
                        </span>
                        <span className="truncate">{s.title}</span>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        {hasCode && (
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isVerified ? "bg-emerald-400" : "bg-amber-400"
                            }`}
                          />
                        )}
                        <span className="text-[10px] text-slate-500 uppercase">{s.type}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Slide Presentation Stage & Verification Details (8 cols) */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          {deck && activeSlide ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col">
              {/* Slide Presentation Header Bar */}
              <div className="bg-slate-950/80 border-b border-slate-800 px-6 py-3.5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded">
                    Slide {activeSlideIndex + 1} of {deck.slides.length} ({activeSlide.id})
                  </span>
                  <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-0.5 rounded uppercase font-semibold">
                    {activeSlide.type}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={regenerateCurrentSlide}
                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-2.5 py-1.5 rounded flex items-center gap-1.5 transition"
                    title="Regenerate this single slide with isolated re-verification"
                  >
                    <RotateCw className="w-3.5 h-3.5 text-indigo-400" />
                    Regenerate Slide
                  </button>
                  <button
                    onClick={() => setShowUpgradeModal(true)}
                    className="text-xs bg-indigo-900/40 hover:bg-indigo-900/60 text-indigo-300 border border-indigo-700/50 px-2.5 py-1.5 rounded flex items-center gap-1.5 transition"
                  >
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    Upgrade Stack
                  </button>
                </div>
              </div>

              {/* Slide Preview Canvas (16:9 aspect) */}
              <div className="p-8 bg-slate-950/40 min-h-[460px] flex flex-col justify-between border-b border-slate-800">
                <div>
                  <h2 className="text-2xl font-bold tracking-tight text-white mb-6">
                    {activeSlide.title}
                  </h2>

                  {/* Bullets List */}
                  {activeSlide.bullets && activeSlide.bullets.length > 0 && (
                    <ul className="space-y-3 mb-6">
                      {activeSlide.bullets.map((b: string, i: number) => (
                        <li key={i} className="flex items-start gap-3 text-sm text-slate-200">
                          <span className="text-indigo-400 mt-1">✦</span>
                          <span>{b}</span>
                        </li>
                      ))}
                    </ul>
                  )}

                  {/* Code Card with Verification Badge */}
                  {activeSlide.code && activeSlide.code.length > 0 && (
                    <div className="rounded-lg border border-slate-800 bg-slate-950 overflow-hidden mt-4">
                      <div className="bg-slate-900/90 px-4 py-2 border-b border-slate-800 flex items-center justify-between">
                        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                          <Code2 className="w-4 h-4 text-indigo-400" />
                          <span>
                            {activeSlide.code[0].lang} ({activeSlide.code[0].version}) ·{" "}
                            {activeSlide.code[0].kind}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {activeSlide.code[0].verified === "passed" ? (
                            <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-2.5 py-0.5 rounded-full flex items-center gap-1 font-semibold">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              VERIFIED PASSED (1 att)
                            </span>
                          ) : (
                            <span className="text-xs bg-amber-500/20 text-amber-400 border border-amber-500/40 px-2.5 py-0.5 rounded-full flex items-center gap-1 font-semibold">
                              <AlertTriangle className="w-3.5 h-3.5" />
                              UNVERIFIED
                            </span>
                          )}
                        </div>
                      </div>
                      <pre className="p-4 text-xs font-mono text-emerald-300 overflow-x-auto leading-relaxed">
                        <code>{activeSlide.code[0].source}</code>
                      </pre>
                    </div>
                  )}

                  {/* Diagram Presentation */}
                  {activeSlide.diagram && (
                    <div className="mt-4 p-4 rounded-lg bg-slate-900/60 border border-slate-800">
                      <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider block mb-2">
                        Visual Architecture Diagram
                      </span>
                      <pre className="text-xs font-mono text-sky-300 bg-slate-950 p-3 rounded border border-slate-800">
                        {typeof activeSlide.diagram === "object" && activeSlide.diagram.source
                          ? activeSlide.diagram.source
                          : activeSlide.diagram}
                      </pre>
                    </div>
                  )}
                </div>

                {/* Speaker Notes */}
                {activeSlide.notes && (
                  <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-start gap-2.5 text-xs text-slate-400 bg-slate-900/40 p-3 rounded-lg">
                    <BookOpen className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    <div>
                      <strong className="text-slate-300 mr-1">Trainer Delivery Notes:</strong>
                      {activeSlide.notes}
                    </div>
                  </div>
                )}
              </div>

              {/* Bottom Pagination controls */}
              <div className="bg-slate-950 px-6 py-3 flex items-center justify-between">
                <button
                  disabled={activeSlideIndex === 0}
                  onClick={() => setActiveSlideIndex(activeSlideIndex - 1)}
                  className="text-xs text-slate-400 hover:text-white disabled:opacity-30 transition"
                >
                  ← Previous Slide
                </button>
                <span className="text-xs text-slate-500 font-mono">
                  {activeSlideIndex + 1} / {deck.slides.length}
                </span>
                <button
                  disabled={activeSlideIndex === deck.slides.length - 1}
                  onClick={() => setActiveSlideIndex(activeSlideIndex + 1)}
                  className="text-xs text-slate-400 hover:text-white disabled:opacity-30 transition"
                >
                  Next Slide →
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-500">
              No deck loaded. Click "Load Sample Deck" or generate a new deck.
            </div>
          )}

          {/* Exercise Prover Card ("Tests Must Bite") */}
          {deck && deck.exercises && deck.exercises.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
                    Dual-Prover Exercise Verification ("Tests Must Bite")
                  </h3>
                </div>
                <span className="text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2.5 py-0.5 rounded-full font-semibold">
                  Contract: Proven
                </span>
              </div>

              {deck.exercises.map((ex: any) => (
                <div key={ex.id} className="space-y-3">
                  <div className="text-xs text-slate-300 font-semibold">{ex.title}</div>
                  <p className="text-xs text-slate-400">{ex.description}</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="bg-slate-950 p-3 rounded-lg border border-emerald-900/30">
                      <div className="flex items-center justify-between text-emerald-400 font-semibold mb-1">
                        <span>1. Reference Solution</span>
                        <span>✓ Passes Unit Tests</span>
                      </div>
                      <p className="text-slate-400 text-[11px]">
                        Instructor reference implementation successfully executes all test cases.
                      </p>
                    </div>

                    <div className="bg-slate-950 p-3 rounded-lg border border-red-900/30">
                      <div className="flex items-center justify-between text-red-400 font-semibold mb-1">
                        <span>2. Naive Buggy Solution</span>
                        <span>✓ Caught & Fails Tests</span>
                      </div>
                      <p className="text-slate-400 text-[11px]">
                        Flawed code missing active filter was successfully rejected by test suite.
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Verification Report Modal */}
      {showReportModal && report && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-3xl w-full p-6 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-sky-400" />
                Zero-Trust Sandbox Verification Audit
              </h3>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-4 gap-3">
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                <div className="text-xs text-slate-400">Total Snippets</div>
                <div className="text-xl font-bold text-white">{report.total_snippets}</div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                <div className="text-xs text-slate-400">Sandbox Passed</div>
                <div className="text-xl font-bold text-emerald-400">{report.passed}</div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                <div className="text-xs text-slate-400">Pass Rate</div>
                <div className="text-xl font-bold text-indigo-400">
                  {report.verification_rate_pct}%
                </div>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                <div className="text-xs text-slate-400">Proven Exercises</div>
                <div className="text-xl font-bold text-sky-400">
                  {report.exercises_proven?.length || 1}
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs uppercase font-semibold text-slate-400">Execution Telemetry</h4>
              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400">
                    <tr>
                      <th className="p-2.5">Snippet</th>
                      <th className="p-2.5">Runtime</th>
                      <th className="p-2.5">Status</th>
                      <th className="p-2.5">Duration</th>
                      <th className="p-2.5">Attempts</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {report.execution_summary?.map((row: any) => (
                      <tr key={row.snippet_id} className="hover:bg-slate-800/40">
                        <td className="p-2.5 font-mono text-indigo-300">{row.snippet_id}</td>
                        <td className="p-2.5">
                          {row.lang} {row.version}
                        </td>
                        <td className="p-2.5">
                          <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-[11px] font-semibold">
                            PASSED
                          </span>
                        </td>
                        <td className="p-2.5 font-mono text-slate-300">{row.duration_ms} ms</td>
                        <td className="p-2.5">{row.attempts || 1}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <a
                href={`${API_BASE}/decks/${deck.deck_id}/report?format=html`}
                target="_blank"
                rel="noreferrer"
                className="text-xs bg-slate-800 hover:bg-slate-700 text-white px-3 py-2 rounded flex items-center gap-1.5 transition"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                View Full HTML Report
              </a>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Code Verification & Self-Healing Theater Modal */}
      {showTheaterModal && (
        <div className="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-5xl w-full p-6 shadow-2xl space-y-5 max-h-[92vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/20">
                  <Sparkles className="w-6 h-6 text-amber-300" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white tracking-tight">
                      AI Code Verification & Self-Healing Theater
                    </h3>
                    <span className="text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full font-semibold uppercase">
                      Controlled Failure Demo
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Watch Pandavs detect, repair, and re-verify faulty code automatically in real time.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowTheaterModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scenario Selector & Controls */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold uppercase text-slate-400 tracking-wider">
                  Scenario:
                </span>
                {(["python_add", "python_boundary", "python_syntax"] as const).map((id) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => {
                      setTheaterExample(id);
                      setTheaterStage("idle");
                      setTheaterProgress(0);
                      setTheaterVerifiedStatus("idle");
                      setTheaterRepairedCode("");
                      setTheaterMeta(null);
                      setTheaterLogs([
                        `[Preset Selected] ${THEATER_PRESETS[id].name}. Click "Watch AI Fix Its Own Code" to launch.`
                      ]);
                    }}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition ${
                      theaterExample === id
                        ? "border-indigo-500 bg-indigo-500/20 text-indigo-300 font-semibold"
                        : "border-slate-800 bg-slate-900 text-slate-400 hover:text-white"
                    }`}
                  >
                    {THEATER_PRESETS[id].name}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setTheaterStage("idle");
                    setTheaterProgress(0);
                    setTheaterVerifiedStatus("idle");
                    setTheaterRepairedCode("");
                    setTheaterMeta(null);
                    setTheaterLogs([
                      "[Theater Ready] Click 'Watch AI Fix Its Own Code' to launch real execution pipeline."
                    ]);
                  }}
                  className="text-xs border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-lg flex items-center gap-1.5 transition"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Reset
                </button>
                <button
                  type="button"
                  onClick={startTheaterDemo}
                  disabled={theaterRunning}
                  className="text-xs bg-gradient-to-r from-indigo-600 via-purple-600 to-emerald-600 hover:from-indigo-500 hover:to-emerald-500 disabled:opacity-50 text-white font-semibold px-4 py-2 rounded-lg flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition"
                >
                  {theaterRunning ? (
                    <>
                      <RotateCw className="w-4 h-4 animate-spin" />
                      <span>Verifying in Sandbox...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Watch AI Fix Its Own Code</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Pipeline Timeline */}
            <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                <span className="uppercase tracking-wider text-[11px] font-semibold text-slate-400">
                  Live Pipeline Timeline
                </span>
                <span className="font-bold text-indigo-400 font-mono">{theaterProgress}%</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-1">
                <div className={`p-2.5 rounded-lg border text-center space-y-1 transition-all ${
                  theaterStage !== "idle" ? "border-emerald-500 bg-emerald-950/60" : "border-slate-800 bg-slate-900"
                }`}>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 1</div>
                  <div className="text-xs font-semibold text-slate-300">Faulty Code</div>
                  <div className="text-[10px] text-emerald-400">Loaded</div>
                </div>

                <div className={`p-2.5 rounded-lg border text-center space-y-1 transition-all ${
                  theaterStage === "executing_original"
                    ? "border-indigo-500 bg-indigo-950/60 shadow-md shadow-indigo-500/20"
                    : theaterProgress >= 45
                    ? "border-slate-700 bg-slate-800/80"
                    : "border-slate-800 bg-slate-900"
                }`}>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 2</div>
                  <div className="text-xs font-semibold text-slate-300">Sandbox Test</div>
                  <div className="text-[10px] text-slate-400">
                    {theaterStage === "executing_original" ? "Executing..." : theaterProgress >= 45 ? "Executed" : "Pending"}
                  </div>
                </div>

                <div className={`p-2.5 rounded-lg border text-center space-y-1 transition-all ${
                  theaterStage === "verification_failed"
                    ? "border-rose-500 bg-rose-950/60 shadow-md shadow-rose-500/20"
                    : theaterProgress >= 65
                    ? "border-slate-700 bg-slate-800/80"
                    : "border-slate-800 bg-slate-900"
                }`}>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 3</div>
                  <div className="text-xs font-semibold text-slate-300">Failure Trace</div>
                  <div className="text-[10px] text-rose-400">
                    {theaterProgress >= 45 ? "Error Caught" : "Pending"}
                  </div>
                </div>

                <div className={`p-2.5 rounded-lg border text-center space-y-1 transition-all ${
                  theaterStage === "repairing"
                    ? "border-amber-500 bg-amber-950/60 shadow-md shadow-amber-500/20"
                    : theaterProgress >= 85
                    ? "border-emerald-500 bg-emerald-950/60"
                    : "border-slate-800 bg-slate-900"
                }`}>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 4</div>
                  <div className="text-xs font-semibold text-slate-300">Self-Healing</div>
                  <div className="text-[10px] text-amber-400">
                    {theaterStage === "repairing" ? "Repairing..." : theaterProgress >= 85 ? "Repaired" : "Pending"}
                  </div>
                </div>

                <div className={`p-2.5 rounded-lg border text-center space-y-1 transition-all ${
                  theaterStage === "executing_repair"
                    ? "border-indigo-500 bg-indigo-950/60 shadow-md shadow-indigo-500/20"
                    : theaterProgress >= 95
                    ? "border-emerald-500 bg-emerald-950/60"
                    : "border-slate-800 bg-slate-900"
                }`}>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 5</div>
                  <div className="text-xs font-semibold text-slate-300">Re-Verification</div>
                  <div className="text-[10px] text-emerald-400">
                    {theaterStage === "executing_repair" ? "Testing..." : theaterProgress >= 95 ? "Passed" : "Pending"}
                  </div>
                </div>

                <div className={`p-2.5 rounded-lg border text-center space-y-1 transition-all ${
                  theaterVerifiedStatus === "passed"
                    ? "border-emerald-500 bg-emerald-950/60 shadow-md shadow-emerald-500/20"
                    : theaterVerifiedStatus === "failed"
                    ? "border-rose-500 bg-rose-950/60"
                    : "border-slate-800 bg-slate-900"
                }`}>
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step 6</div>
                  <div className="text-xs font-semibold text-slate-300">VERIFIED</div>
                  <div className="text-[10px] text-emerald-400">
                    {theaterVerifiedStatus === "passed" ? "100% Passed" : theaterVerifiedStatus === "failed" ? "Failed" : "Pending"}
                  </div>
                </div>
              </div>
            </div>

            {/* Code Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-950 rounded-xl border border-rose-500/30 overflow-hidden flex flex-col">
                <div className="bg-rose-950/40 border-b border-rose-500/30 px-3.5 py-2.5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                    <span className="text-xs font-bold text-rose-300 tracking-tight">Original Code — Failed</span>
                  </div>
                  <span className="text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/40 px-2 py-0.5 rounded font-mono font-semibold">
                    Assertion Failure
                  </span>
                </div>
                <pre className="p-4 text-xs font-mono text-rose-200 overflow-x-auto leading-relaxed flex-1 bg-slate-950/70">
                  <code>{THEATER_PRESETS[theaterExample].code}</code>
                </pre>
              </div>

              <div className="bg-slate-950 rounded-xl border border-emerald-500/30 overflow-hidden flex flex-col">
                <div className="bg-emerald-950/40 border-b border-emerald-500/30 px-3.5 py-2.5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span className="text-xs font-bold text-emerald-300 tracking-tight">Corrected Code — Re-Verified</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold border ${
                    theaterVerifiedStatus === "passed"
                      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                      : "bg-slate-800 text-slate-400 border-slate-700"
                  }`}>
                    {theaterVerifiedStatus === "passed" ? "VERIFIED — PASSED" : "Awaiting Repair"}
                  </span>
                </div>
                <pre className="p-4 text-xs font-mono text-emerald-300 overflow-x-auto leading-relaxed flex-1 bg-slate-950/70">
                  <code>
                    {theaterRepairedCode ||
                      "# Corrected implementation will appear here after Self-Healing\n# Watch AI fix this code in real time..."}
                  </code>
                </pre>
              </div>
            </div>

            {/* Sandbox Console */}
            <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden shadow-inner">
              <div className="bg-slate-900/90 border-b border-slate-800 px-3.5 py-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80"></span>
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80"></span>
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">sandbox-runner@pandavs (Python 3.12 Isolated Execution)</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">Live Telemetry</span>
              </div>
              <div className="p-3.5 text-[11px] font-mono text-slate-300 bg-slate-950/90 h-44 overflow-y-auto space-y-1 leading-relaxed">
                {theaterLogs.map((log, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-slate-600 select-none">[{idx + 1}]</span>
                    <span className={log.includes("ERROR") || log.includes("FAILED") ? "text-rose-400" : log.includes("PASSED") || log.includes("VERIFIED") ? "text-emerald-400 font-semibold" : "text-slate-300"}>
                      {log}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Verification Result Banner */}
            <div className={`p-4 rounded-xl border flex flex-wrap items-center justify-between gap-3 ${
              theaterVerifiedStatus === "passed"
                ? "border-emerald-500/50 bg-emerald-950/40 shadow-lg shadow-emerald-500/10"
                : theaterVerifiedStatus === "failed"
                ? "border-rose-500/50 bg-rose-950/40"
                : "border-slate-800 bg-slate-950"
            }`}>
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  theaterVerifiedStatus === "passed"
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                    : theaterVerifiedStatus === "failed"
                    ? "bg-rose-500/20 text-rose-400 border border-rose-500/40"
                    : "bg-slate-800 text-slate-400"
                }`}>
                  {theaterVerifiedStatus === "passed" ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : theaterVerifiedStatus === "failed" ? (
                    <XCircle className="w-5 h-5" />
                  ) : (
                    <ShieldCheck className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <div className="text-xs font-bold text-white uppercase tracking-wider">
                    {theaterVerifiedStatus === "passed"
                      ? "VERIFIED — ALL TESTS PASSED"
                      : theaterVerifiedStatus === "failed"
                      ? "VERIFICATION FAILED"
                      : "Ready for Sandbox Execution"}
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {theaterVerifiedStatus === "passed"
                      ? "Repaired code met 100% of specification assertions in clean subprocess sandbox."
                      : "All tests run inside an isolated subprocess with zero mock data."}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 flex-wrap text-[11px] font-mono">
                <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-md">
                  Provider: {theaterMeta?.repair_provider || "—"}
                </span>
                <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-md">
                  Duration: {theaterMeta?.duration_ms ? `${theaterMeta.duration_ms} ms` : "—"}
                </span>
                <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-md">
                  Sandbox: Python 3.12 Isolated
                </span>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                <span className="text-emerald-400">●</span>
                <span>Genuine subprocess execution: Real assertions, real error trace, real repair.</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowTheaterModal(false)}
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg transition"
                >
                  Close Theater
                </button>
                <button
                  type="button"
                  onClick={addTheaterToDeck}
                  disabled={theaterVerifiedStatus !== "passed" || isAddingToDeck}
                  className="text-xs bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:hover:bg-emerald-600 text-white font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 shadow-md transition"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>{isAddingToDeck ? "Adding..." : "Add Verified Example to Deck"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-400" />
              Automated Framework Upgrade & Re-Verification
            </h3>
            <p className="text-xs text-slate-400">
              Upgrades the entire presentation deck from legacy framework versions (e.g. Spring Boot 2.7 javax.*) to Spring Boot 3.3 (jakarta.*), re-verifying every snippet in the sandbox.
            </p>

            {upgradeDiff ? (
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2 text-xs">
                <div className="text-emerald-400 font-semibold">✓ Upgrade Completed</div>
                <div>Modified Snippets: {upgradeDiff.changes_count}</div>
                <div className="text-slate-400 text-[11px]">
                  All javax.* annotations migrated to jakarta.* and validated against Spring Boot 3.3.
                </div>
              </div>
            ) : null}

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => {
                  setShowUpgradeModal(false);
                  setUpgradeDiff(null);
                }}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded transition"
              >
                Cancel
              </button>
              <button
                onClick={handleUpgrade}
                className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-4 py-2 rounded transition"
              >
                Run Upgrade & Verify
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
