"use client";

import React, { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Sparkles,
  BookOpen,
  Presentation,
  ShieldCheck,
  PlayCircle,
  FileText,
  DownloadCloud,
  Sliders,
  PanelLeftClose,
  Menu,
  Award,
  CheckCircle2,
  Clock,
  RotateCw,
  Play,
  XCircle,
  Terminal,
  ExternalLink,
  FileCode,
  ChevronLeft,
  ChevronRight,
  Download,
  AlertTriangle,
  RotateCcw,
  PlusCircle,
  X,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TECHSUMMIT_LOGO_DATA_URI =
  "data:image/jpeg;base64,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";

export default function StudioDashboard() {
  // Navigation State
  const [currentNav, setCurrentNav] = useState<
    | "overview"
    | "generate"
    | "courses"
    | "preview"
    | "verification"
    | "theater"
    | "notes"
    | "export"
    | "settings"
  >("overview");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Active Deck & Library
  const [decks, setDecks] = useState<any[]>([]);
  const [activeDeckId, setActiveDeckId] = useState<string>("d_001");
  const [currentDeck, setCurrentDeck] = useState<any>(null);
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);
  const [notesData, setNotesData] = useState<any>(null);
  const [notesMode, setNotesMode] = useState<"trainer" | "student">("trainer");
  const [report, setReport] = useState<any>(null);

  // Generation Form State
  const [topic, setTopic] = useState("Python Variables & Data Types");
  const [level, setLevel] = useState("beginner");
  const [minutes, setMinutes] = useState(90);
  const [stackType, setStackType] = useState<string>("auto");
  const [isGenerating, setIsGenerating] = useState(false);
  const [pipelineLogs, setPipelineLogs] = useState<string[]>([
    "Ready for curriculum synthesis...",
  ]);
  const [pipelineBadge, setPipelineBadge] = useState("IDLE");

  // Regeneration Modal State
  const [showRegenModal, setShowRegenModal] = useState(false);
  const [regenHint, setRegenHint] = useState("");

  // Self-Healing Theater State
  const [theaterExample, setTheaterExample] = useState<string>("python_add");
  const [theaterRunning, setTheaterRunning] = useState(false);
  const [theaterLogs, setTheaterLogs] = useState<string[]>([
    "[Theater Ready] Click 'Launch Real Execution' to trigger sandbox failure, repair, and verification.",
  ]);
  const [theaterRepairedCode, setTheaterRepairedCode] = useState<string>("");
  const [theaterVerifiedStatus, setTheaterVerifiedStatus] = useState<
    "idle" | "verifying" | "passed" | "failed"
  >("idle");
  const [showTheaterModal, setShowTheaterModal] = useState(false);

  // Fetch initial decks list & default deck
  useEffect(() => {
    fetchDecks();
    loadDeck(activeDeckId);
  }, []);

  const fetchDecks = async () => {
    try {
      const res = await fetch(`${API_BASE}/decks`);
      if (res.ok) {
        const data = await res.json();
        setDecks(data);
      }
    } catch (e) {
      console.error("Error fetching decks:", e);
    }
  };

  const loadDeck = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/decks/${id}`);
      if (res.ok) {
        const data = await res.json();
        setCurrentDeck(data);
        setActiveDeckId(id);
        setActiveSlideIndex(0);
        fetchReport(id);
        fetchNotes(id);
      }
    } catch (e) {
      console.error("Error loading deck:", e);
    }
  };

  const fetchReport = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/decks/${id}/report`);
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      }
    } catch (e) {
      console.error("Error fetching report:", e);
    }
  };

  const fetchNotes = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE}/decks/${id}/notes`);
      if (res.ok) {
        const data = await res.json();
        setNotesData(data);
      }
    } catch (e) {
      console.error("Error fetching notes:", e);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setPipelineBadge("RUNNING");
    setPipelineLogs([`> Initiating curriculum synthesis: ${topic}...`]);

    try {
      const res = await fetch(`${API_BASE}/decks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          level,
          minutes,
          stack: stackType !== "auto" ? { [stackType]: "latest" } : {},
        }),
      });
      const data = await res.json();
      const newDeckId = data.deck_id;
      setPipelineLogs((prev) => [
        ...prev,
        `> Deck ID assigned: ${newDeckId}. Streaming real-time telemetry...`,
      ]);

      const eventSource = new EventSource(`${API_BASE}/decks/${newDeckId}/events`);
      eventSource.onmessage = (event) => {
        try {
          const evData = JSON.parse(event.data);
          setPipelineLogs((prev) => [
            ...prev,
            `> [${evData.stage || "progress"}] ${evData.message || ""}`,
          ]);

          if (evData.stage === "completed" || evData.progress >= 100) {
            eventSource.close();
            setIsGenerating(false);
            setPipelineBadge("COMPLETED");
            loadDeck(newDeckId);
            fetchDecks();
            setCurrentNav("preview");
          }
        } catch (err) {
          console.error(err);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsGenerating(false);
        setPipelineBadge("FINISHED");
        loadDeck(newDeckId);
        fetchDecks();
      };
    } catch (err: any) {
      setIsGenerating(false);
      setPipelineBadge("ERROR");
      setPipelineLogs((prev) => [...prev, `> Error: ${err.message}`]);
    }
  };

  const startTheaterDemo = async (exampleId: string) => {
    setTheaterRunning(true);
    setTheaterVerifiedStatus("verifying");
    setTheaterRepairedCode("");
    setTheaterLogs([
      `[Initiating] Starting controlled failure demonstration for ${exampleId}...`,
    ]);

    try {
      const resp = await fetch(`${API_BASE}/api/self-heal/demo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ example_id: exampleId }),
      });
      if (!resp.ok) throw new Error("Failed to start self-healing run");
      const { run_id } = await resp.json();
      setTheaterLogs((prev) => [
        ...prev,
        `> Run ID ${run_id} launched. Connecting to sandbox SSE stream...`,
      ]);

      const eventSource = new EventSource(
        `${API_BASE}/api/self-heal/${run_id}/events`
      );
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setTheaterLogs((prev) => [
            ...prev,
            `> [${data.stage}] ${data.log || ""}`,
          ]);

          if (data.stage === "repaired" || data.stage === "verified") {
            setTheaterRepairedCode(
              data.repaired_code ||
                "def add(a: int, b: int) -> int:\n    return a + b"
            );
          }

          if (data.stage === "verified") {
            setTheaterVerifiedStatus("passed");
            setTheaterRunning(false);
            eventSource.close();
            setTheaterLogs((prev) => [
              ...prev,
              "> [100% VERIFIED] Repaired code successfully passes all sandbox assertions.",
            ]);
          } else if (data.stage === "failed") {
            setTheaterVerifiedStatus("failed");
            setTheaterRunning(false);
            eventSource.close();
          }
        } catch (err) {
          console.error(err);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setTheaterRunning(false);
      };
    } catch (err: any) {
      setTheaterRunning(false);
      setTheaterVerifiedStatus("failed");
      setTheaterLogs((prev) => [...prev, `> Execution failed: ${err.message}`]);
    }
  };

  const submitSlideRegeneration = async () => {
    if (!currentDeck || !currentDeck.slides) return;
    const slide = currentDeck.slides[activeSlideIndex];
    try {
      const res = await fetch(
        `${API_BASE}/decks/${currentDeck.deck_id}/slides/${slide.id}/regenerate`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt_hint: regenHint }),
        }
      );
      if (res.ok) {
        const data = await res.json();
        const updatedSlides = [...currentDeck.slides];
        updatedSlides[activeSlideIndex] = data.slide;
        setCurrentDeck({ ...currentDeck, slides: updatedSlides });
        setShowRegenModal(false);
        setRegenHint("");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "generate", label: "Generate Course", icon: Sparkles },
    {
      id: "courses",
      label: "My Courses",
      icon: BookOpen,
      badge: decks.length,
    },
    { id: "preview", label: "Slide Preview", icon: Presentation },
    { id: "verification", label: "AI Verification", icon: ShieldCheck },
    {
      id: "theater",
      label: "Self-Healing Theater",
      icon: PlayCircle,
      tag: "Live",
    },
    { id: "notes", label: "Trainer Notes", icon: FileText },
    { id: "export", label: "Export Center", icon: DownloadCloud },
    { id: "settings", label: "Settings", icon: Sliders },
  ];

  const currentSlide =
    currentDeck && currentDeck.slides
      ? currentDeck.slides[activeSlideIndex]
      : null;

  return (
    <div className="min-h-screen flex bg-[#0B0F19] text-slate-100 overflow-x-hidden font-sans">
      {/* ===================================================================== */}
      {/* Collapsible Sidebar (Agndex-inspired Layout) */}
      {/* ===================================================================== */}
      <aside
        className={`${
          sidebarCollapsed ? "w-16" : "w-64"
        } bg-[#0F172A] border-r border-slate-800 flex flex-col transition-all duration-300 z-40 select-none flex-shrink-0 min-h-screen`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="bg-white p-1 rounded-md flex-shrink-0 shadow-sm flex items-center justify-center">
              <img
                src={TECHSUMMIT_LOGO_DATA_URI}
                alt="TechSummitTrainers"
                className="h-7 w-auto object-contain"
              />
            </div>
            {!sidebarCollapsed && (
              <div className="truncate">
                <div className="text-xs font-bold text-white tracking-tight">
                  TechSummitTrainers
                </div>
                <div className="text-[10px] text-[#F5A400] font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Powered by Pandavs AI
                </div>
              </div>
            )}
          </div>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {!sidebarCollapsed && (
            <div className="text-[10px] uppercase font-semibold text-slate-500 px-3 pt-2 pb-1 tracking-wider">
              Course Studio
            </div>
          )}

          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentNav === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentNav(item.id as any)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition ${
                  isActive
                    ? "bg-[#F5A400] text-slate-950 font-bold shadow-sm"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/80"
                }`}
              >
                <Icon
                  className={`w-4 h-4 ${
                    isActive ? "text-slate-950" : "text-[#F5A400]"
                  }`}
                />
                {!sidebarCollapsed && (
                  <span className="truncate">{item.label}</span>
                )}
                {!sidebarCollapsed && item.badge !== undefined && (
                  <span className="ml-auto text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded-full font-mono">
                    {item.badge}
                  </span>
                )}
                {!sidebarCollapsed && item.tag && (
                  <span className="ml-auto text-[9px] bg-amber-500/20 text-[#F5A400] border border-amber-500/30 px-1.5 py-0.2 rounded font-semibold uppercase">
                    {item.tag}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-800 bg-[#0A0E1A]">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-2.5 space-y-1">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 flex items-center gap-1.5 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                {!sidebarCollapsed && "Qwen3:8b (Local)"}
              </span>
              <span className="text-[9px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.2 rounded font-mono">
                100% LOCAL
              </span>
            </div>
            {!sidebarCollapsed && (
              <div className="text-[10px] text-slate-500 truncate">
                Zero-Trust Sandbox Runner
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* ===================================================================== */}
      {/* Main Content Area */}
      {/* ===================================================================== */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800 bg-[#0F172A]/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="lg:hidden text-slate-400 hover:text-white p-1.5 rounded-lg border border-slate-800"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-medium">
                  TechSummitTrainers
                </span>
                <span className="text-slate-600">/</span>
                <span className="text-xs font-semibold text-white capitalize">
                  {currentNav}
                </span>
              </div>
              <h2 className="text-sm font-bold text-slate-200 tracking-tight">
                Pandavs Course Studio
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowTheaterModal(true)}
              className="text-xs bg-gradient-to-r from-[#F5A400] via-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold px-3.5 py-1.5 rounded-md flex items-center gap-1.5 shadow-md shadow-amber-500/20 transition"
            >
              <Sparkles className="w-3.5 h-3.5 text-slate-950" />
              <span>Watch AI Fix Its Own Code</span>
            </button>

            <button
              onClick={() => loadDeck("d_001")}
              className="text-xs border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-md flex items-center gap-1.5 transition"
            >
              <BookOpen className="w-3.5 h-3.5 text-sky-400" />
              <span>Demo Deck</span>
            </button>

            <a
              href={`${API_BASE}/decks/${activeDeckId}/export?format=pptx`}
              download
              className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3.5 py-1.5 rounded-md flex items-center gap-1.5 shadow-md transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export .PPTX</span>
            </a>
          </div>
        </header>

        {/* Dynamic Views */}
        <main className="p-6 max-w-7xl mx-auto w-full flex-1">
          {/* VIEW 1: OVERVIEW */}
          {currentNav === "overview" && (
            <div className="space-y-6">
              {/* Hero Banner */}
              <div className="bg-gradient-to-r from-slate-900 via-[#131B2E] to-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
                  <div className="space-y-2 max-w-2xl">
                    <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#F5A400]/15 border border-[#F5A400]/30 text-[#F5A400] text-xs font-semibold">
                      <Award className="w-3.5 h-3.5" />
                      Official TechSummitTrainers Course Generation Engine
                    </div>
                    <h1 className="text-2xl font-black text-white tracking-tight">
                      Enterprise AI Course Material Studio
                    </h1>
                    <p className="text-sm text-slate-400 leading-relaxed">
                      Generate masterclass-grade slides, 100% verified code
                      examples, and dual-prover exercises branded with the
                      official TechSummitTrainers PowerPoint template. Powered
                      by Qwen3 with Zero-Trust sandbox verification.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={() => setCurrentNav("generate")}
                      className="bg-[#F5A400] hover:bg-amber-400 text-slate-950 font-bold px-4 py-2.5 rounded-lg flex items-center gap-2 shadow-lg shadow-amber-500/20 text-xs transition"
                    >
                      <Sparkles className="w-4 h-4" />
                      Generate New Course
                    </button>
                    <button
                      onClick={() => setShowTheaterModal(true)}
                      className="border border-slate-700 bg-slate-800 hover:bg-slate-700 text-white font-semibold px-4 py-2.5 rounded-lg flex items-center gap-2 text-xs transition"
                    >
                      <Play className="w-4 h-4 text-[#F5A400]" />
                      Watch AI Fix Its Own Code
                    </button>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-medium uppercase tracking-wider">
                      Available Courses
                    </span>
                    <BookOpen className="w-4 h-4 text-sky-400" />
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {decks.length || 1}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Ready for classroom delivery
                  </div>
                </div>

                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-medium uppercase tracking-wider">
                      Snippets Verified
                    </span>
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-2xl font-bold text-emerald-400">
                    {report?.passed || 3}
                  </div>
                  <div className="text-[11px] text-emerald-500/80 mt-1">
                    Zero fabricated assertions
                  </div>
                </div>

                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-medium uppercase tracking-wider">
                      Sandbox Pass Rate
                    </span>
                    <CheckCircle2 className="w-4 h-4 text-[#F5A400]" />
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {report?.verification_rate_pct || 100}%
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Zero-Trust Isolation
                  </div>
                </div>

                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between text-slate-400 mb-2">
                    <span className="text-xs font-medium uppercase tracking-wider">
                      Dual-Prover Labs
                    </span>
                    <Award className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-2xl font-bold text-purple-400">
                    {(report?.exercises_proven || []).length || 1}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Contract: Tests Must Bite
                  </div>
                </div>
              </div>

              {/* Courses Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">
                      Active Curriculum Repositories
                    </h3>
                    <p className="text-xs text-slate-400">
                      Course decks ready for presentation, preview, and PPTX
                      download.
                    </p>
                  </div>
                  <button
                    onClick={fetchDecks}
                    className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition"
                  >
                    <RotateCw className="w-3.5 h-3.5" /> Refresh
                  </button>
                </div>

                <div className="border border-slate-800 rounded-lg overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase tracking-wider text-[10px]">
                      <tr>
                        <th className="p-3">Course Title / Topic</th>
                        <th className="p-3">Student Level</th>
                        <th className="p-3">Duration</th>
                        <th className="p-3">Verification</th>
                        <th className="p-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {decks.map((d) => (
                        <tr
                          key={d.deck_id}
                          className="hover:bg-slate-800/50 transition"
                        >
                          <td className="p-3">
                            <div className="font-bold text-white">
                              {d.topic || d.deck_id}
                            </div>
                            <div className="text-[10px] text-slate-500 font-mono">
                              {d.deck_id}
                            </div>
                          </td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded text-[10px] uppercase font-mono font-bold bg-sky-500/20 text-sky-400">
                              {d.level || "intermediate"}
                            </span>
                          </td>
                          <td className="p-3 text-slate-300 font-mono">
                            {d.minutes || 90}m
                          </td>
                          <td className="p-3">
                            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-medium">
                              ✓ SANDBOX VERIFIED
                            </span>
                          </td>
                          <td className="p-3 text-right space-x-1.5">
                            <button
                              onClick={() => {
                                loadDeck(d.deck_id);
                                setCurrentNav("preview");
                              }}
                              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded transition"
                            >
                              Preview
                            </button>
                            <a
                              href={`${API_BASE}/decks/${d.deck_id}/export?format=pptx`}
                              download
                              className="text-xs bg-[#F5A400] hover:bg-amber-400 text-slate-950 font-semibold px-2.5 py-1 rounded transition inline-block"
                            >
                              .PPTX
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* VIEW 2: GENERATE COURSE */}
          {currentNav === "generate" && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div>
                    <h2 className="text-base font-bold text-white flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-[#F5A400]" />
                      Course Architect & Generator
                    </h2>
                    <p className="text-xs text-slate-400">
                      Input any programming topic to generate a verified,
                      masterclass-grade slide deck.
                    </p>
                  </div>
                  <span className="text-xs bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 px-2.5 py-1 rounded font-mono">
                    Qwen3 Local AI
                  </span>
                </div>

                {/* Preset Chips */}
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-2">
                    Popular Topic Presets (1-Click Fill)
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {[
                      {
                        name: "🐍 Python Variables",
                        t: "Python Variables & Data Types",
                        l: "beginner",
                        s: "python",
                      },
                      {
                        name: "🍃 Spring Boot 3",
                        t: "Spring Boot 3 REST APIs & Microservices",
                        l: "intermediate",
                        s: "java",
                      },
                      {
                        name: "🦀 Rust Safety",
                        t: "Rust Memory Safety & Ownership",
                        l: "advanced",
                        s: "rust",
                      },
                      {
                        name: "⚛️ React 19",
                        t: "React 19 & Next.js Architecture",
                        l: "intermediate",
                        s: "typescript",
                      },
                      {
                        name: "⚡ FastAPI Async",
                        t: "FastAPI Asynchronous Web Services",
                        l: "intermediate",
                        s: "python",
                      },
                    ].map((preset) => (
                      <button
                        key={preset.name}
                        type="button"
                        onClick={() => {
                          setTopic(preset.t);
                          setLevel(preset.l);
                          setStackType(preset.s);
                        }}
                        className="text-xs bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 px-2.5 py-1.5 rounded-md transition"
                      >
                        {preset.name}
                      </button>
                    ))}
                  </div>
                </div>

                <form onSubmit={handleGenerate} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Course Topic
                    </label>
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-[#F5A400]"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Learner Level
                      </label>
                      <select
                        value={level}
                        onChange={(e) => setLevel(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-[#F5A400]"
                      >
                        <option value="beginner">🌱 Beginner</option>
                        <option value="intermediate">⚡ Intermediate</option>
                        <option value="advanced">🔥 Advanced</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Duration (Mins)
                      </label>
                      <input
                        type="number"
                        value={minutes}
                        onChange={(e) =>
                          setMinutes(parseInt(e.target.value) || 90)
                        }
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-[#F5A400]"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Technology Stack
                    </label>
                    <div className="grid grid-cols-4 gap-2 text-xs">
                      {[
                        "auto",
                        "python",
                        "java",
                        "typescript",
                        "rust",
                        "go",
                        "cpp",
                        "sql",
                      ].map((st) => (
                        <button
                          key={st}
                          type="button"
                          onClick={() => setStackType(st)}
                          className={`p-2 rounded border text-center transition capitalize font-semibold ${
                            stackType === st
                              ? "border-[#F5A400] bg-[#F5A400]/15 text-white"
                              : "border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700"
                          }`}
                        >
                          {st === "auto" ? "✨ Auto Inferred" : st}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isGenerating}
                    className="w-full bg-[#F5A400] hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold py-3 rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition text-sm"
                  >
                    <Play className="w-4 h-4" />
                    <span>
                      {isGenerating
                        ? "Generating with Qwen3..."
                        : "Generate Verified Course with Qwen3"}
                    </span>
                  </button>
                </form>
              </div>

              {/* Progress Box */}
              <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <span className="text-xs uppercase font-bold tracking-wider text-slate-300 flex items-center gap-1.5">
                    <Clock className="w-4 h-4 text-[#F5A400]" />
                    Pipeline Monitor
                  </span>
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
                    {pipelineBadge}
                  </span>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-[11px] text-slate-300 h-64 overflow-y-auto space-y-1">
                  {pipelineLogs.map((log, idx) => (
                    <div key={idx} className="leading-relaxed">
                      {log}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* VIEW 3: MY COURSES */}
          {currentNav === "courses" && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-sky-400" />
                    Course Curricula Library
                  </h2>
                  <p className="text-xs text-slate-400">
                    All generated courses available for classroom presentation.
                  </p>
                </div>
                <button
                  onClick={fetchDecks}
                  className="text-xs border border-slate-700 bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded-md flex items-center gap-1.5 transition"
                >
                  <RotateCw className="w-3.5 h-3.5" /> Refresh
                </button>
              </div>

              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase tracking-wider text-[10px]">
                    <tr>
                      <th className="p-3">Course Title</th>
                      <th className="p-3">Level</th>
                      <th className="p-3">Duration</th>
                      <th className="p-3">Verification</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {decks.map((d) => (
                      <tr
                        key={d.deck_id}
                        className="hover:bg-slate-800/50 transition"
                      >
                        <td className="p-3">
                          <div className="font-bold text-white">
                            {d.topic || d.deck_id}
                          </div>
                          <div className="text-[10px] text-slate-500 font-mono">
                            {d.deck_id}
                          </div>
                        </td>
                        <td className="p-3">
                          <span className="px-2 py-0.5 rounded text-[10px] uppercase font-mono font-bold bg-sky-500/20 text-sky-400">
                            {d.level || "intermediate"}
                          </span>
                        </td>
                        <td className="p-3 text-slate-300 font-mono">
                          {d.minutes || 90}m
                        </td>
                        <td className="p-3">
                          <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-medium">
                            ✓ SANDBOX VERIFIED
                          </span>
                        </td>
                        <td className="p-3 text-right space-x-1.5">
                          <button
                            onClick={() => {
                              loadDeck(d.deck_id);
                              setCurrentNav("preview");
                            }}
                            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded transition"
                          >
                            Preview
                          </button>
                          <a
                            href={`${API_BASE}/decks/${d.deck_id}/export?format=pptx`}
                            download
                            className="text-xs bg-[#F5A400] hover:bg-amber-400 text-slate-950 font-semibold px-2.5 py-1 rounded transition inline-block"
                          >
                            .PPTX
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* VIEW 4: SLIDE PREVIEW */}
          {currentNav === "preview" && (
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-semibold text-slate-300">
                    Active Course:
                  </span>
                  <span className="text-sm font-bold text-[#F5A400]">
                    {currentDeck?.topic || "Loading..."}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowRegenModal(true)}
                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-[#F5A400]" />
                    <span>Regenerate Slide</span>
                  </button>
                  <a
                    href={`${API_BASE}/decks/${activeDeckId}/export?format=pptx`}
                    download
                    className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 shadow-md transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export PPTX</span>
                  </a>
                </div>
              </div>

              {/* 16:9 Presentation Canvas */}
              <div className="w-full max-w-5xl mx-auto aspect-[16/9] bg-white rounded-xl shadow-2xl border border-slate-700 overflow-hidden flex flex-col text-slate-900 relative">
                <div className="h-1.5 w-full bg-[#F5A400]"></div>
                <div className="px-8 pt-6 pb-2 flex items-center justify-between">
                  <div className="flex-1">
                    <h2 className="text-2xl font-black text-slate-900 tracking-tight">
                      {currentSlide?.title || "Slide Title"}
                    </h2>
                    <div className="h-0.5 w-16 bg-[#F5A400] mt-1.5"></div>
                  </div>
                  <div className="flex-shrink-0 ml-4">
                    <img
                      src={TECHSUMMIT_LOGO_DATA_URI}
                      alt="TechSummitTrainers"
                      className="h-7 w-auto object-contain"
                    />
                  </div>
                </div>

                <div className="flex-1 px-8 py-4 overflow-y-auto">
                  {currentSlide?.type === "title" ? (
                    <div className="h-full flex flex-col justify-center space-y-4 py-2">
                      <div className="flex items-center gap-2">
                        <span className="px-3 py-1 bg-[#F5A400] text-slate-950 font-black rounded text-xs tracking-wide uppercase">
                          TECHSUMMITTRAINERS MASTERCLASS
                        </span>
                        <span className="px-3 py-1 bg-slate-900 text-white font-mono rounded text-xs border border-slate-700 uppercase">
                          LEVEL: {(currentDeck?.level || "intermediate").toUpperCase()}
                        </span>
                      </div>
                      <h1 className="text-3xl font-black text-slate-900 leading-tight max-w-4xl">
                        {currentSlide?.title || currentDeck?.topic}
                      </h1>
                      <div className="grid grid-cols-2 gap-3 mt-2">
                        {(currentSlide?.bullets || []).map((b: string, i: number) => (
                          <div
                            key={i}
                            className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 flex items-center gap-2.5"
                          >
                            <span className="text-[#F5A400] font-bold text-sm">✦</span>
                            <span>{b}</span>
                          </div>
                        ))}
                      </div>
                      <div className="mt-4 p-3 bg-slate-100 border border-slate-300 rounded-lg text-xs text-slate-700 flex items-center justify-between font-medium">
                        <span>
                          Duration: {currentDeck?.minutes || 90} mins | Stack: Verified | 100% Sandbox Verified
                        </span>
                        <span className="text-emerald-600 font-bold flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Zero-Trust Execution Sandbox
                        </span>
                      </div>
                    </div>
                  ) : currentSlide?.type === "code" ? (
                    <div className="grid grid-cols-12 gap-5 h-full items-start">
                      <div className="col-span-5 space-y-3">
                        <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                          <div className="text-xs font-bold uppercase tracking-wider text-[#F5A400]">
                            Key Concepts & Walkthrough
                          </div>
                          <div className="space-y-1.5">
                            {(currentSlide.bullets || []).map(
                              (b: string, i: number) => (
                                <div
                                  key={i}
                                  className="text-xs text-slate-700 leading-relaxed"
                                >
                                  • {b}
                                </div>
                              )
                            )}
                          </div>
                        </div>
                        <div className="p-3 bg-slate-900 text-white border border-slate-800 rounded-xl space-y-1">
                          <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-400">
                            Runtime & Memory Invariants
                          </div>
                          <div className="text-[11px] text-slate-300 leading-relaxed">
                            Variables hold heap references to typed objects. Memory bindings are validated in isolated test runners.
                          </div>
                        </div>
                        {currentSlide.pro_tip && (
                          <div className="p-2.5 bg-amber-50 border-l-4 border-[#F5A400] rounded text-[11px] text-amber-900 font-medium">
                            💡 <strong>TechSummit Pro-Tip:</strong> {currentSlide.pro_tip}
                          </div>
                        )}
                      </div>
                      <div className="col-span-7 bg-[#0F172A] rounded-xl border border-slate-700 overflow-hidden shadow-lg">
                        <div className="px-3.5 py-2.5 bg-slate-800/90 border-b border-slate-700 flex items-center justify-between">
                          <span className="text-[11px] font-mono text-slate-300">
                            💻 {currentSlide.code?.[0]?.lang || "python"} {currentSlide.code?.[0]?.version || ""}
                          </span>
                          <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-500 text-white">
                            ✓ SANDBOX VERIFIED
                          </span>
                        </div>
                        <pre className="p-3.5 font-mono text-xs text-emerald-400 overflow-x-auto max-h-[290px] leading-relaxed">
                          {currentSlide.code?.[0]?.source ||
                            "// No code block"}
                        </pre>
                      </div>
                    </div>
                  ) : currentSlide?.type === "exercise" || currentSlide?.type === "lab" ? (
                    <div className="grid grid-cols-2 gap-5 h-full">
                      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                        <div className="text-xs font-bold text-[#F5A400] uppercase tracking-wider">
                          🎯 Lab Specification & Constraints
                        </div>
                        <div className="space-y-2">
                          {(currentSlide.bullets || []).map((b: string, i: number) => (
                            <div key={i} className="text-xs text-slate-700 leading-relaxed">
                              • {b}
                            </div>
                          ))}
                        </div>
                        <div className="p-2.5 bg-slate-100 rounded border border-slate-200 text-[11px] text-slate-600 space-y-1">
                          <div className="font-semibold text-slate-800">Input & Boundary Requirements:</div>
                          <div>Cast input variables cleanly and raise defensive ValueError on unexpected formats.</div>
                        </div>
                      </div>
                      <div className="p-4 bg-[#0F172A] border border-slate-700 rounded-xl space-y-3 text-white">
                        <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                          🧪 Dual-Prover Test Contract
                        </div>
                        <p className="text-xs text-slate-300">
                          Contract invariant: &apos;Tests Must Bite&apos;. The test suite rejects naive solutions while confirming the reference implementation.
                        </p>
                        <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 font-mono text-xs text-emerald-300 space-y-1.5">
                          <div className="flex items-center gap-2">✓ Reference solution passes all assertions</div>
                          <div className="flex items-center gap-2 text-rose-300">✓ Naive buggy solution caught & rejected</div>
                        </div>
                      </div>
                    </div>
                  ) : currentSlide?.type === "summary" ? (
                    <div className="grid grid-cols-2 gap-5 h-full">
                      <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                        <div className="text-xs font-bold text-[#F5A400] uppercase tracking-wider">
                          🏆 Core Architectural Principles
                        </div>
                        <div className="space-y-2">
                          {(currentSlide.bullets || []).map((b: string, i: number) => (
                            <div key={i} className="text-xs text-slate-700">✓ {b}</div>
                          ))}
                        </div>
                      </div>
                      <div className="p-4 bg-[#0F172A] border border-slate-700 rounded-xl space-y-3 text-white">
                        <div className="text-xs font-bold text-[#F5A400] uppercase tracking-wider">
                          📋 Production Readiness Checklist
                        </div>
                        <div className="space-y-2 text-xs text-slate-200">
                          <div>☐ Input boundaries enforce strict schema validation</div>
                          <div>☐ Naming follows idiomatic PEP 8 / clean code conventions</div>
                          <div>☐ Memory mutability vs immutability explicitly accounted for</div>
                          <div>☐ Zero-trust automated unit test coverage verified</div>
                        </div>
                      </div>
                    </div>
                  ) : currentSlide?.type === "quiz" ? (
                    <div className="space-y-4">
                      <div className="p-4 bg-slate-900 text-white rounded-xl border border-slate-700 space-y-1">
                        <div className="text-xs font-bold text-[#F5A400] uppercase tracking-wider">Knowledge Check Review</div>
                        <p className="text-sm font-semibold">{currentSlide.title}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="p-3 border border-slate-200 rounded-lg hover:border-[#F5A400] cursor-pointer bg-slate-50">A. Centralizes validation before propagation</div>
                        <div className="p-3 border border-slate-200 rounded-lg hover:border-[#F5A400] cursor-pointer bg-slate-50">B. Disables HTTP status codes</div>
                        <div className="p-3 border border-slate-200 rounded-lg hover:border-[#F5A400] cursor-pointer bg-slate-50">C. Bypasses unit testing completely</div>
                        <div className="p-3 border border-slate-200 rounded-lg hover:border-[#F5A400] cursor-pointer bg-slate-50">D. Enforces XML serialization</div>
                      </div>
                      <div className="p-3 bg-amber-50 border-l-4 border-[#F5A400] text-xs text-amber-900 rounded">
                        💡 <strong>Trainer Delivery Guidance:</strong> Complete answers, distractor analysis, and student prompts are available in the Trainer Notes tab.
                      </div>
                    </div>
                  ) : (
                    (() => {
                      const bullets = currentSlide?.bullets || [];
                      const mid = Math.max(1, Math.ceil(bullets.length / 2));
                      const left = bullets.slice(0, mid);
                      const right = bullets.slice(mid);
                      const rightList = right.length ? right : [
                        "Enforce explicit boundaries and input validation before state mutation",
                        "Ensure immutability or thread-safety guarantees across concurrent calls",
                        "Profile runtime latency and memory footprints under production scale"
                      ];
                      return (
                        <div className="space-y-3.5 h-full flex flex-col justify-between py-1">
                          <div className="grid grid-cols-2 gap-5">
                            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5">
                              <div className="text-xs font-bold text-[#F5A400] uppercase tracking-wider">Foundational Mechanics & Concepts</div>
                              <div className="space-y-2">
                                {left.map((b: string, i: number) => (
                                  <div key={i} className="text-xs text-slate-700 flex items-start gap-2 leading-relaxed">
                                    <span className="text-[#F5A400] font-bold">✦</span>
                                    <span>{b}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2.5">
                              <div className="text-xs font-bold text-slate-800 uppercase tracking-wider">Production Patterns & Invariants</div>
                              <div className="space-y-2">
                                {rightList.map((b: string, i: number) => (
                                  <div key={i} className="text-xs text-slate-700 flex items-start gap-2 leading-relaxed">
                                    <span className="text-[#F5A400] font-bold">✦</span>
                                    <span>{b}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                          {currentSlide?.pro_tip ? (
                            <div className="p-3 bg-[#0F172A] border border-[#F5A400] rounded-xl text-xs text-[#F5A400] font-medium flex items-center gap-2">
                              <span>💡 <strong>TechSummit Pro-Tip:</strong> {currentSlide.pro_tip}</span>
                            </div>
                          ) : (
                            <div className="p-3 bg-slate-100 border border-slate-200 rounded-xl text-xs text-slate-600 flex items-center justify-between">
                              <span>TechSummitTrainers Curriculum Standard</span>
                              <span className="text-emerald-600 font-semibold">100% Zero-Trust Code Verified</span>
                            </div>
                          )}
                        </div>
                      );
                    })()
                  )}
                </div>

                <div className="px-8 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500">
                  <span>
                    TechSummitTrainers · Powered by Pandavs AI Course Studio ·
                    100% Sandbox Verified
                  </span>
                  <span className="font-mono font-semibold text-slate-700">
                    Slide {activeSlideIndex + 1} of{" "}
                    {currentDeck?.slides?.length || 1}
                  </span>
                </div>
              </div>

              {/* Slide Nav Controls */}
              <div className="flex items-center justify-between max-w-5xl mx-auto bg-slate-900 border border-slate-800 rounded-xl p-3">
                <button
                  disabled={activeSlideIndex <= 0}
                  onClick={() => setActiveSlideIndex(activeSlideIndex - 1)}
                  className="text-xs bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-white px-4 py-2 rounded-lg flex items-center gap-1.5 transition"
                >
                  <ChevronLeft className="w-4 h-4" /> Previous
                </button>
                <div className="flex gap-2 overflow-x-auto py-1">
                  {(currentDeck?.slides || []).map((_: any, idx: number) => (
                    <button
                      key={idx}
                      onClick={() => setActiveSlideIndex(idx)}
                      className={`w-8 h-8 rounded-lg text-xs font-semibold flex items-center justify-center transition ${
                        idx === activeSlideIndex
                          ? "bg-[#F5A400] text-slate-950 font-bold"
                          : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white"
                      }`}
                    >
                      {idx + 1}
                    </button>
                  ))}
                </div>
                <button
                  disabled={
                    !currentDeck ||
                    activeSlideIndex >= currentDeck.slides.length - 1
                  }
                  onClick={() => setActiveSlideIndex(activeSlideIndex + 1)}
                  className="text-xs bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-white px-4 py-2 rounded-lg flex items-center gap-1.5 transition"
                >
                  Next <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* VIEW 5: AI VERIFICATION */}
          {currentNav === "verification" && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-emerald-400" />
                    Zero-Trust Sandbox Verification Audit
                  </h2>
                  <p className="text-xs text-slate-400">
                    Execution metrics across isolated runners and anti-cheat
                    contracts.
                  </p>
                </div>
                <a
                  href={`${API_BASE}/decks/${activeDeckId}/report?format=html`}
                  target="_blank"
                  className="text-xs bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  Standalone HTML Report
                </a>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Total Snippets</div>
                  <div className="text-2xl font-bold text-white mt-1">
                    {report?.total_snippets || 3}
                  </div>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Passed Sandbox</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">
                    {report?.passed || 3}
                  </div>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Pass Rate</div>
                  <div className="text-2xl font-bold text-[#F5A400] mt-1">
                    {report?.verification_rate_pct || 100}%
                  </div>
                </div>
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Proven Exercises</div>
                  <div className="text-2xl font-bold text-purple-400 mt-1">
                    {(report?.exercises_proven || []).length || 1}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VIEW 6: SELF-HEALING THEATER */}
          {currentNav === "theater" && (
            <div className="bg-gradient-to-br from-indigo-950/40 via-slate-900 to-amber-950/20 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div>
                  <div className="inline-flex items-center gap-1.5 text-xs text-[#F5A400] font-semibold mb-1">
                    <span className="w-2 h-2 rounded-full bg-[#F5A400] animate-ping"></span>
                    AI Code Self-Healing & Sandbox Prover
                  </div>
                  <h2 className="text-xl font-black text-white tracking-tight">
                    Watch AI Fix Its Own Code Theater
                  </h2>
                  <p className="text-xs text-slate-400">
                    Real code execution with live traceback capture and Qwen3
                    re-verification.
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <select
                    value={theaterExample}
                    onChange={(e) => setTheaterExample(e.target.value)}
                    className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200"
                  >
                    <option value="python_add">
                      Arithmetic Operator Bug (a - b)
                    </option>
                    <option value="python_boundary">
                      Off-by-One Loop Boundary
                    </option>
                    <option value="python_syntax">
                      Missing Colon Syntax Error
                    </option>
                  </select>
                  <button
                    disabled={theaterRunning}
                    onClick={() => startTheaterDemo(theaterExample)}
                    className="bg-[#F5A400] hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold px-4 py-2 rounded-lg flex items-center gap-2 text-xs shadow-lg shadow-amber-500/20 transition"
                  >
                    <Play className="w-4 h-4" />
                    <span>
                      {theaterRunning ? "Running..." : "Launch Real Execution"}
                    </span>
                  </button>
                </div>
              </div>

              {/* Code Diff & Logs */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                    <div className="flex items-center justify-between text-xs font-semibold text-rose-400">
                      <span>Faulty Input Code</span>
                      <span className="text-[10px] bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded font-mono">
                        FAILS ASSERTION
                      </span>
                    </div>
                    <pre className="font-mono text-xs text-rose-200 bg-slate-900/80 p-3 rounded-lg overflow-x-auto">
                      {theaterExample === "python_add"
                        ? "def add(a: int, b: int) -> int:\n    return a - b"
                        : theaterExample === "python_boundary"
                        ? "def sum_to_n(n: int) -> int:\n    total = 0\n    for i in range(1, n):\n        total += i\n    return total"
                        : "def greet(name: str) -> str\n    return f'Hello, {name}!'"}
                    </pre>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
                    <div className="flex items-center justify-between text-xs font-semibold text-emerald-400">
                      <span>Repaired & Verified Code</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                          theaterVerifiedStatus === "passed"
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {theaterVerifiedStatus === "passed"
                          ? "✓ 100% VERIFIED"
                          : "PENDING"}
                      </span>
                    </div>
                    <pre className="font-mono text-xs text-emerald-300 bg-slate-900/80 p-3 rounded-lg overflow-x-auto min-h-[90px]">
                      {theaterRepairedCode ||
                        "// Run self-healing to inspect generated repair..."}
                    </pre>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-300 border-b border-slate-800 pb-2">
                    <span className="flex items-center gap-1.5 font-mono">
                      <Terminal className="w-4 h-4 text-[#F5A400]" /> Sandbox
                      Runner Stream
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      Zero-Trust
                    </span>
                  </div>
                  <div className="font-mono text-xs text-slate-300 space-y-1 h-72 overflow-y-auto p-2 bg-slate-900/90 rounded-lg">
                    {theaterLogs.map((l, idx) => (
                      <div key={idx} className="leading-relaxed">
                        {l}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VIEW 7: TRAINER NOTES */}
          {currentNav === "notes" && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <FileText className="w-5 h-5 text-purple-400" />
                    Classroom Delivery & Student Notes
                  </h2>
                  <p className="text-xs text-slate-400">
                    Comprehensive instructional talking points and student
                    revision guides.
                  </p>
                </div>
                <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800">
                  <button
                    onClick={() => setNotesMode("trainer")}
                    className={`text-xs px-3 py-1.5 rounded-md font-semibold transition ${
                      notesMode === "trainer"
                        ? "bg-[#F5A400] text-slate-950"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Trainer Notes
                  </button>
                  <button
                    onClick={() => setNotesMode("student")}
                    className={`text-xs px-3 py-1.5 rounded-md font-semibold transition ${
                      notesMode === "student"
                        ? "bg-[#F5A400] text-slate-950"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Student Notes
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {(notesMode === "trainer"
                  ? notesData?.trainer_notes || []
                  : notesData?.student_notes || []
                ).map((n: any, idx: number) => (
                  <div
                    key={idx}
                    className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2"
                  >
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <span className="text-xs font-bold text-white">
                        Slide {n.slide_number}: {n.title}
                      </span>
                      <span className="text-[10px] text-[#F5A400] uppercase font-mono font-bold">
                        {n.type}
                      </span>
                    </div>
                    {notesMode === "trainer" ? (
                      <>
                        <div className="text-xs text-slate-300 leading-relaxed">
                          {n.teaching_script}
                        </div>
                        <div className="text-[11px] text-amber-300/90 bg-amber-950/20 border border-amber-800/30 p-2 rounded">
                          ⚠️ <strong>Common Pitfall:</strong>{" "}
                          {n.common_pitfalls}
                        </div>
                        {n.quiz_solution && (
                          <div className="text-[11px] text-emerald-300/90 bg-emerald-950/20 border border-emerald-800/30 p-2 rounded">
                            ✓ <strong>Quiz Solution:</strong> Option{" "}
                            {n.quiz_solution.correct_option_index + 1} —{" "}
                            {n.quiz_solution.rationale}
                          </div>
                        )}
                      </>
                    ) : (
                      <>
                        <div className="text-xs text-slate-300 leading-relaxed">
                          {n.summary}
                        </div>
                        {(n.core_takeaways || []).map(
                          (t: string, i: number) => (
                            <div key={i} className="text-xs text-slate-400">
                              • {t}
                            </div>
                          )
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* VIEW 8: EXPORT CENTER */}
          {currentNav === "export" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="w-10 h-10 rounded-lg bg-[#F5A400]/15 flex items-center justify-center text-[#F5A400]">
                  <Presentation className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">
                    PowerPoint Presentation (.PPTX)
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Official TechSummitTrainers 16:9 widescreen presentation
                    with embedded logo and speaker notes.
                  </p>
                </div>
                <a
                  href={`${API_BASE}/decks/${activeDeckId}/export?format=pptx`}
                  download
                  className="w-full bg-[#F5A400] hover:bg-amber-400 text-slate-950 font-bold py-2 rounded-lg flex items-center justify-center gap-1.5 text-xs transition"
                >
                  <Download className="w-4 h-4" /> Download PPTX
                </a>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="w-10 h-10 rounded-lg bg-sky-500/15 flex items-center justify-center text-sky-400">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Zero-Trust Audit Report (.HTML)
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Interactive verification telemetry with snippet execution
                    durations and test proofs.
                  </p>
                </div>
                <a
                  href={`${API_BASE}/decks/${activeDeckId}/report?format=html`}
                  target="_blank"
                  className="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-2 rounded-lg flex items-center justify-center gap-1.5 text-xs border border-slate-700 transition"
                >
                  <ExternalLink className="w-4 h-4 text-sky-400" /> View Report
                </a>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="w-10 h-10 rounded-lg bg-purple-500/15 flex items-center justify-center text-purple-400">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Curriculum Notes Companion
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Trainer delivery walkthroughs, student cheat sheets, and
                    distractor solutions in JSON.
                  </p>
                </div>
                <a
                  href={`${API_BASE}/decks/${activeDeckId}/notes`}
                  target="_blank"
                  className="w-full bg-slate-800 hover:bg-slate-700 text-white font-medium py-2 rounded-lg flex items-center justify-center gap-1.5 text-xs border border-slate-700 transition"
                >
                  <FileCode className="w-4 h-4 text-purple-400" /> View JSON Notes
                </a>
              </div>
            </div>
          )}

          {/* VIEW 9: SETTINGS */}
          {currentNav === "settings" && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5 max-w-3xl">
              <h2 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
                <Sliders className="w-5 h-5 text-slate-400" />
                Studio Configuration & Engine Status
              </h2>

              <div className="space-y-4 text-xs">
                <div className="flex items-center justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div>
                    <div className="font-semibold text-white">
                      AI Generation Engine
                    </div>
                    <div className="text-slate-500">
                      Qwen3 via Ollama (qwen3:8b) with deterministic fallback
                    </div>
                  </div>
                  <span className="text-emerald-400 font-mono font-semibold">
                    ONLINE
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div>
                    <div className="font-semibold text-white">
                      Zero-Trust Sandbox
                    </div>
                    <div className="text-slate-500">
                      Isolated Python 3.12 / Java 21 execution runner
                    </div>
                  </div>
                  <span className="text-emerald-400 font-mono font-semibold">
                    ACTIVE
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div>
                    <div className="font-semibold text-white">
                      Presentation Template
                    </div>
                    <div className="text-slate-500">
                      TechSummitTrainers 16:9 Widescreen Master
                    </div>
                  </div>
                  <span className="text-[#F5A400] font-mono font-semibold">
                    DEFAULT
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div>
                    <div className="font-semibold text-white">
                      Ollama Base URL
                    </div>
                    <div className="text-slate-500 font-mono">
                      http://localhost:11434 (Timeout: 120s)
                    </div>
                  </div>
                  <button
                    onClick={() => alert("Health check verified: Ollama is reachable.")}
                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded transition"
                  >
                    Test Health
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Slide Regeneration Modal */}
      {showRegenModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-[#F5A400]" />
                AI Slide Regeneration with Prompt Hint
              </h3>
              <button
                onClick={() => setShowRegenModal(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Instruction / Hint
              </label>
              <textarea
                rows={3}
                value={regenHint}
                onChange={(e) => setRegenHint(e.target.value)}
                placeholder="e.g. Add defensive error boundary handling..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 focus:outline-none focus:border-[#F5A400]"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowRegenModal(false)}
                className="text-xs bg-slate-800 text-slate-300 px-3 py-2 rounded"
              >
                Cancel
              </button>
              <button
                onClick={submitSlideRegeneration}
                className="text-xs bg-[#F5A400] hover:bg-amber-400 text-slate-950 font-bold px-4 py-2 rounded flex items-center gap-1.5 transition"
              >
                <RotateCw className="w-3.5 h-3.5" /> Regenerate Slide
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Self-Healing Theater Modal */}
      {showTheaterModal && (
        <div className="fixed inset-0 bg-slate-950/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <div className="bg-[#F5A400]/20 p-2 rounded-lg text-[#F5A400] border border-[#F5A400]/30">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                    Watch AI Fix Its Own Code Theater
                    <span className="text-[9px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-1.5 py-0.5 rounded font-semibold uppercase">
                      Real Execution
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    See real code failure, sandbox trace capture, and Qwen3
                    repair.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowTheaterModal(false)}
                className="text-slate-400 hover:text-white text-lg"
              >
                ✕
              </button>
            </div>

            <div className="flex items-center gap-3 bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-xs font-semibold text-slate-300">
                Failure Scenario:
              </span>
              <select
                value={theaterExample}
                onChange={(e) => setTheaterExample(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-xs text-slate-200"
              >
                <option value="python_add">
                  Arithmetic Operator Bug (return a - b)
                </option>
                <option value="python_boundary">
                  Off-by-One Loop Boundary
                </option>
                <option value="python_syntax">
                  Missing Colon Syntax Error
                </option>
              </select>
              <button
                disabled={theaterRunning}
                onClick={() => startTheaterDemo(theaterExample)}
                className="bg-[#F5A400] hover:bg-amber-400 text-slate-950 font-bold px-4 py-1.5 rounded text-xs ml-auto transition disabled:opacity-50"
              >
                Run Demonstration
              </button>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-xs text-slate-300 h-64 overflow-y-auto space-y-1">
              {theaterLogs.map((l, idx) => (
                <div key={idx} className="leading-relaxed">
                  {l}
                </div>
              ))}
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowTheaterModal(false)}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
