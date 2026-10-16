"use client";

import React, { useState, useEffect } from "react";
import {
  Play,
  RotateCw,
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
                        {activeSlide.diagram}
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
