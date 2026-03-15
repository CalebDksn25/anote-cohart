"use client";

import { useState } from "react";
import { extractTranscript, ExtractionApiError } from "@/lib/api";
import { ExtractionResponse, ValidationErrorDetail } from "@/types/extraction";
import UploadForm from "@/components/UploadForm";
import ResultsPanel from "@/components/ResultsPanel";
import LoadingSpinner from "@/components/LoadingSpinner";
import ErrorAlert from "@/components/ErrorAlert";

type AppState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ExtractionResponse }
  | { status: "error"; message: string; validationErrors?: string[] };

const EXAMPLE_LINES: { type: string; text: string }[] = [
  { type: "key",      text: "Date: 2024-03-15" },
  { type: "label",    text: "Meeting: Q1 Product Review" },
  { type: "blank",    text: "" },
  { type: "speaker",  text: "Alice:" },
  { type: "dialogue", text: "  Let's kick off. Bob, can you own the dashboard redesign" },
  { type: "dialogue", text: "  and get mockups ready by Wednesday?" },
  { type: "speaker",  text: "Bob:" },
  { type: "dialogue", text: "  Absolutely, I'll have them ready." },
  { type: "speaker",  text: "Alice:" },
  { type: "dialogue", text: "  Great. We've also decided to deprecate the v1 API" },
  { type: "dialogue", text: "  starting April 1st — that's final." },
  { type: "speaker",  text: "Carol:" },
  { type: "dialogue", text: "  I'll update the migration guide by next Friday." },
  { type: "speaker",  text: "Alice:" },
  { type: "dialogue", text: "  Carol, can you also schedule a follow-up with the" },
  { type: "dialogue", text: "  design team sometime next week?" },
  { type: "speaker",  text: "Carol:" },
  { type: "dialogue", text: "  Will do, I'll send calendar invites by tomorrow." },
];

function TranscriptExample() {
  return (
    <pre
      className="text-xs leading-6 overflow-x-auto"
      style={{ fontFamily: "var(--font-geist-mono)" }}
    >
      {EXAMPLE_LINES.map((line, i) => {
        const lineNum = (i + 1).toString().padStart(2, " ");
        const colorClass =
          line.type === "key"      ? "transcript-line-key"      :
          line.type === "label"    ? "transcript-line-label"    :
          line.type === "speaker"  ? "transcript-line-speaker"  :
          line.type === "dialogue" ? "transcript-line-dialogue" :
          "transcript-line-label";

        return (
          <div key={i} className="flex">
            <span style={{ color: "#2d4a6a", userSelect: "none", minWidth: "2rem" }}>
              {lineNum}
            </span>
            <span className={line.text === "" ? "" : colorClass}>
              {line.text === "" ? "\n" : line.text + "\n"}
            </span>
          </div>
        );
      })}
    </pre>
  );
}

export default function Home() {
  const [state, setState] = useState<AppState>({ status: "idle" });

  async function handleSubmit(file: File) {
    setState({ status: "loading" });
    try {
      const data = await extractTranscript(file);
      setState({ status: "success", data });
    } catch (err) {
      if (err instanceof ExtractionApiError) {
        const detail = err.detail;
        if (typeof detail === "object" && detail !== null && "errors" in detail) {
          const d = detail as ValidationErrorDetail;
          setState({
            status: "error",
            message: d.message ?? err.message,
            validationErrors: d.errors,
          });
        } else {
          setState({ status: "error", message: err.message });
        }
      } else {
        setState({
          status: "error",
          message: err instanceof Error ? err.message : "Unknown error",
        });
      }
    }
  }

  function handleReset() {
    setState({ status: "idle" });
  }

  return (
    <main className="min-h-screen" style={{ background: "var(--background)" }}>
      {/* ── Nav ── */}
      <nav
        className="border-b px-6 py-4 sticky top-0 z-50"
        style={{
          borderColor: "var(--card-border)",
          background: "rgba(6, 14, 26, 0.9)",
          backdropFilter: "blur(16px)",
        }}
      >
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span
              className="text-xl font-bold tracking-tight text-white"
              style={{ fontFamily: "var(--font-syne)" }}
            >
              anote
            </span>
          </div>
          <div
            className="px-3 py-1 rounded-full text-xs"
            style={{
              border: "1px solid var(--card-border)",
              color: "var(--muted)",
            }}
          >
            Powered by GPT-4o-mini
          </div>
        </div>
      </nav>

      {/* ── IDLE: full landing page ── */}
      {state.status === "idle" && (
        <>
          {/* Hero */}
          <section className="relative overflow-hidden">
            {/* Background atmosphere */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              <div
                className="absolute -top-32 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full"
                style={{ background: "radial-gradient(ellipse, rgba(34,211,238,0.07) 0%, transparent 70%)" }}
              />
              <div
                className="absolute top-0 left-0 right-0 h-px"
                style={{ background: "linear-gradient(90deg, transparent, rgba(34,211,238,0.2), transparent)" }}
              />
            </div>

            <div className="mx-auto max-w-5xl px-4 pt-24 pb-20 text-center relative">
              {/* Pill badge */}
              <div
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium mb-10 animate-fade-up"
                style={{
                  border: "1px solid rgba(34,211,238,0.25)",
                  background: "rgba(34,211,238,0.06)",
                  color: "#67e8f9",
                }}
              >
                <span
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ background: "#22d3ee", animation: "pulse-dot 2s ease-in-out infinite" }}
                />
                Human-centered AI extraction
              </div>

              <h1
                className="text-5xl sm:text-6xl font-extrabold tracking-tight leading-[1.05] mb-6 animate-fade-up-delay-1"
                style={{ fontFamily: "var(--font-syne)" }}
              >
                <span className="text-white">Stop losing track</span>
                <br />
                <span className="shimmer-gradient">of what was decided.</span>
              </h1>

              <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed animate-fade-up-delay-2">
                Paste a meeting transcript and instantly surface every action item, decision, and follow-up —
                with owners, due dates normalized to ISO format, and the exact quote it came from.
              </p>

              {/* Output type pills */}
              <div className="flex flex-wrap justify-center gap-3 animate-fade-up-delay-3">
                {[
                  { label: "Action Items", dot: "#22d3ee", bg: "rgba(34,211,238,0.06)", border: "rgba(34,211,238,0.2)", color: "#67e8f9" },
                  { label: "Decisions",    dot: "#34d399", bg: "rgba(52,211,153,0.06)",  border: "rgba(52,211,153,0.2)",  color: "#6ee7b7" },
                  { label: "Follow-ups",   dot: "#a78bfa", bg: "rgba(167,139,250,0.06)", border: "rgba(167,139,250,0.2)", color: "#c4b5fd" },
                ].map(({ label, dot, bg, border, color }) => (
                  <span
                    key={label}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium"
                    style={{ background: bg, border: `1px solid ${border}`, color }}
                  >
                    <span className="w-2 h-2 rounded-full" style={{ background: dot }} />
                    {label}
                  </span>
                ))}
              </div>
            </div>
          </section>

          {/* ── What we extract ── */}
          <section className="mx-auto max-w-5xl px-4 pb-20">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                {
                  accent: "#22d3ee",
                  accentBg: "rgba(34,211,238,0.07)",
                  icon: (
                    <svg className="w-5 h-5" fill="none" stroke="#22d3ee" viewBox="0 0 24 24" strokeWidth={1.8}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  ),
                  title: "Action Items",
                  desc: "Tasks explicitly assigned to someone. Each item includes the owner's name and a normalized ISO due date wherever mentioned.",
                  chips: ["Owner", "Due date (ISO)", "Source quote", "Needs review flag"],
                },
                {
                  accent: "#34d399",
                  accentBg: "rgba(52,211,153,0.07)",
                  icon: (
                    <svg className="w-5 h-5" fill="none" stroke="#34d399" viewBox="0 0 24 24" strokeWidth={1.8}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  ),
                  title: "Decisions",
                  desc: "Conclusions or resolutions the group agreed upon — policy changes, go/no-go calls, or finalized plans.",
                  chips: ["Decision text", "Context", "Source quote"],
                },
                {
                  accent: "#a78bfa",
                  accentBg: "rgba(167,139,250,0.07)",
                  icon: (
                    <svg className="w-5 h-5" fill="none" stroke="#a78bfa" viewBox="0 0 24 24" strokeWidth={1.8}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  ),
                  title: "Follow-ups",
                  desc: "Scheduled check-ins, pending clarifications, or items explicitly deferred to a future meeting.",
                  chips: ["Topic", "Assignee", "Timeframe", "Source quote"],
                },
              ].map(({ accent, accentBg, icon, title, desc, chips }) => (
                <div
                  key={title}
                  className="rounded-2xl border p-6 group transition-all duration-200 hover:translate-y-[-2px]"
                  style={{
                    background: "var(--card)",
                    borderColor: "var(--card-border)",
                  }}
                >
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center mb-5"
                    style={{ background: accentBg }}
                  >
                    {icon}
                  </div>
                  <h3
                    className="font-bold text-white mb-2 text-base"
                    style={{ fontFamily: "var(--font-syne)" }}
                  >
                    {title}
                  </h3>
                  <p className="text-sm text-slate-400 leading-relaxed mb-5">{desc}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {chips.map((chip) => (
                      <span
                        key={chip}
                        className="text-xs px-2 py-0.5 rounded-md"
                        style={{
                          background: "rgba(255,255,255,0.04)",
                          border: "1px solid rgba(255,255,255,0.07)",
                          color: "#94a3b8",
                        }}
                      >
                        {chip}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ── How it works ── */}
          <section className="mx-auto max-w-5xl px-4 pb-20">
            <div className="text-center mb-12">
              <h2
                className="text-2xl font-bold text-white"
                style={{ fontFamily: "var(--font-syne)" }}
              >
                How it works
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 relative">
              {/* connector */}
              <div
                className="hidden sm:block absolute top-[22px] left-[calc(16.67%+1.25rem)] right-[calc(16.67%+1.25rem)] h-px"
                style={{ background: "linear-gradient(90deg, rgba(34,211,238,0.3), rgba(34,211,238,0.1), rgba(34,211,238,0.3))" }}
              />
              {[
                {
                  step: "01",
                  title: "Prepare your transcript",
                  desc: "Write up your meeting notes in a plain .txt file. Include a Date: header on line 1 and attribute each speaker by name.",
                },
                {
                  step: "02",
                  title: "Upload & extract",
                  desc: "Drag and drop your file below. The AI reads every line, identifies meaningful items, and normalizes all date references.",
                },
                {
                  step: "03",
                  title: "Review structured output",
                  desc: "Browse action items, decisions, and follow-ups in organized tabs. Click any card to reveal the original source quote.",
                },
              ].map(({ step, title, desc }) => (
                <div key={step} className="flex flex-col items-center text-center relative z-10 px-4">
                  <div
                    className="w-11 h-11 rounded-full flex items-center justify-center mb-5"
                    style={{
                      background: "var(--background)",
                      border: "2px solid rgba(34,211,238,0.4)",
                      boxShadow: "0 0 20px rgba(34,211,238,0.08)",
                    }}
                  >
                    <span
                      className="text-xs font-bold"
                      style={{ color: "#22d3ee", fontFamily: "var(--font-geist-mono)" }}
                    >
                      {step}
                    </span>
                  </div>
                  <h3
                    className="font-semibold text-white mb-2 text-sm"
                    style={{ fontFamily: "var(--font-syne)" }}
                  >
                    {title}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed max-w-[200px]">{desc}</p>
                </div>
              ))}
            </div>
          </section>

          {/* ── Format requirements + example ── */}
          <section className="mx-auto max-w-5xl px-4 pb-20">
            <div
              className="rounded-2xl overflow-hidden"
              style={{ border: "1px solid var(--card-border)" }}
            >
              <div className="grid grid-cols-1 lg:grid-cols-2">
                {/* Requirements panel */}
                <div
                  className="p-8"
                  style={{
                    background: "var(--card)",
                    borderBottom: "1px solid var(--card-border)",
                  }}
                >
                  <div className="flex items-center gap-2.5 mb-7">
                    <div className="w-1 h-5 rounded-full" style={{ background: "#22d3ee" }} />
                    <h2
                      className="text-base font-bold text-white"
                      style={{ fontFamily: "var(--font-syne)" }}
                    >
                      Transcript Format
                    </h2>
                  </div>

                  <div className="space-y-6">
                    {[
                      {
                        badge: "Required",
                        badgeBg: "rgba(34,211,238,0.1)",
                        badgeColor: "#22d3ee",
                        badgeBorder: "rgba(34,211,238,0.2)",
                        label: "Date header — line 1",
                        desc: (
                          <>
                            The very first line must be{" "}
                            <code
                              className="px-1.5 py-0.5 rounded text-xs"
                              style={{ background: "rgba(34,211,238,0.1)", color: "#67e8f9", fontFamily: "var(--font-geist-mono)" }}
                            >
                              Date: YYYY-MM-DD
                            </code>
                            . This is how the extractor resolves relative phrases like{" "}
                            <span style={{ color: "#94a3b8" }}>&ldquo;by Friday&rdquo;</span> or{" "}
                            <span style={{ color: "#94a3b8" }}>&ldquo;next Wednesday&rdquo;</span> into real ISO dates.
                          </>
                        ),
                      },
                      {
                        badge: "Required",
                        badgeBg: "rgba(34,211,238,0.1)",
                        badgeColor: "#22d3ee",
                        badgeBorder: "rgba(34,211,238,0.2)",
                        label: "Plain text (.txt only)",
                        desc: "Upload as a .txt file. No PDF, DOCX, audio, or video — the extractor works on raw text.",
                      },
                      {
                        badge: "Recommended",
                        badgeBg: "rgba(251,191,36,0.08)",
                        badgeColor: "#fbbf24",
                        badgeBorder: "rgba(251,191,36,0.2)",
                        label: "Speaker attribution",
                        desc: (
                          <>
                            Format each turn as{" "}
                            <code
                              className="px-1.5 py-0.5 rounded text-xs"
                              style={{ background: "rgba(255,255,255,0.05)", color: "#7dd3fc", fontFamily: "var(--font-geist-mono)" }}
                            >
                              Name: dialogue
                            </code>
                            . This lets the AI attribute ownership to the correct person.
                          </>
                        ),
                      },
                      {
                        badge: "Optional",
                        badgeBg: "rgba(255,255,255,0.04)",
                        badgeColor: "#64748b",
                        badgeBorder: "rgba(255,255,255,0.08)",
                        label: "Meeting title",
                        desc: (
                          <>
                            A{" "}
                            <code
                              className="px-1.5 py-0.5 rounded text-xs"
                              style={{ background: "rgba(255,255,255,0.05)", color: "#94a3b8", fontFamily: "var(--font-geist-mono)" }}
                            >
                              Meeting: ...
                            </code>{" "}
                            line on line 2 provides helpful context but isn&apos;t required for extraction.
                          </>
                        ),
                      },
                    ].map(({ badge, badgeBg, badgeColor, badgeBorder, label, desc }) => (
                      <div key={label} className="flex gap-3.5">
                        <span
                          className="mt-0.5 text-xs font-semibold px-2 py-0.5 rounded flex-shrink-0 h-fit"
                          style={{
                            background: badgeBg,
                            color: badgeColor,
                            border: `1px solid ${badgeBorder}`,
                            fontFamily: "var(--font-geist-mono)",
                          }}
                        >
                          {badge}
                        </span>
                        <div>
                          <div className="text-sm font-medium text-slate-200 mb-1">{label}</div>
                          <div className="text-xs text-slate-400 leading-relaxed">{desc}</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Ambiguous dates warning */}
                  <div
                    className="mt-7 p-3.5 rounded-xl flex gap-2.5"
                    style={{
                      background: "rgba(251,191,36,0.05)",
                      border: "1px solid rgba(251,191,36,0.15)",
                    }}
                  >
                    <svg
                      className="w-4 h-4 flex-shrink-0 mt-0.5"
                      style={{ color: "#fbbf24" }}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <p className="text-xs leading-relaxed" style={{ color: "rgba(251,191,36,0.8)" }}>
                      Ambiguous due dates like{" "}
                      <code style={{ fontFamily: "var(--font-geist-mono)", color: "#fcd34d" }}>ASAP</code> or{" "}
                      <code style={{ fontFamily: "var(--font-geist-mono)", color: "#fcd34d" }}>next week</code>{" "}
                      are flagged for human review instead of assumed — so nothing slips through silently.
                    </p>
                  </div>
                </div>

                {/* Example transcript */}
                <div
                  className="p-8 lg:border-l"
                  style={{ background: "#040b16", borderColor: "var(--card-border)" }}
                >
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-1 h-5 rounded-full" style={{ background: "#34d399" }} />
                      <h3
                        className="text-sm font-semibold text-slate-300"
                        style={{ fontFamily: "var(--font-syne)" }}
                      >
                        Example transcript
                      </h3>
                    </div>
                    <span
                      className="text-xs"
                      style={{ color: "#2d4a6a", fontFamily: "var(--font-geist-mono)" }}
                    >
                      q1-review.txt
                    </span>
                  </div>
                  <div
                    className="rounded-xl p-4 overflow-auto"
                    style={{ background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.04)" }}
                  >
                    <TranscriptExample />
                  </div>

                  {/* Extraction callouts */}
                  <div className="mt-5 space-y-2.5">
                    {[
                      { color: "#22d3ee", label: "Action item", text: "Bob → dashboard mockups by Wed" },
                      { color: "#22d3ee", label: "Action item", text: "Carol → migration guide by next Fri" },
                      { color: "#34d399", label: "Decision",    text: "v1 API deprecated April 1st" },
                      { color: "#a78bfa", label: "Follow-up",   text: "Design team meeting next week" },
                    ].map(({ color, label, text }) => (
                      <div
                        key={text}
                        className="flex items-center gap-2.5 text-xs rounded-lg px-3 py-2"
                        style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)" }}
                      >
                        <span
                          className="font-semibold flex-shrink-0 px-1.5 py-0.5 rounded text-xs"
                          style={{ background: `${color}15`, color, fontFamily: "var(--font-geist-mono)" }}
                        >
                          {label}
                        </span>
                        <span style={{ color: "#94a3b8" }}>{text}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── Upload CTA ── */}
          <section className="mx-auto max-w-3xl px-4 pb-24" id="upload">
            <div className="text-center mb-8">
              <h2
                className="text-2xl font-bold text-white mb-2"
                style={{ fontFamily: "var(--font-syne)" }}
              >
                Ready to extract?
              </h2>
              <p className="text-sm text-slate-400">
                Drop your .txt transcript below and get structured output in seconds.
              </p>
            </div>
            <div
              className="rounded-2xl border p-6"
              style={{ background: "var(--card)", borderColor: "var(--card-border)" }}
            >
              <UploadForm onSubmit={handleSubmit} disabled={false} />
            </div>
          </section>

          {/* ── Footer ── */}
          <footer
            className="border-t px-6 py-6 text-center text-xs"
            style={{ borderColor: "var(--card-border)", color: "#334155" }}
          >
            anote — built with Human Centered AI
          </footer>
        </>
      )}

      {/* ── Non-idle states (loading / error / success) ── */}
      {state.status !== "idle" && (
        <div className="mx-auto max-w-3xl px-4 py-12 space-y-6">
          {state.status === "loading" && <LoadingSpinner />}

          {state.status === "error" && (
            <>
              <ErrorAlert message={state.message} validationErrors={state.validationErrors} />
              <button
                onClick={handleReset}
                className="w-full rounded-lg border px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:text-white"
                style={{ borderColor: "var(--card-border)", background: "var(--card)" }}
              >
                Try again
              </button>
            </>
          )}

          {state.status === "success" && (
            <>
              <ResultsPanel data={state.data} />
              <button
                onClick={handleReset}
                className="w-full rounded-lg border px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:text-white"
                style={{ borderColor: "var(--card-border)", background: "var(--card)" }}
              >
                Upload another transcript
              </button>
            </>
          )}
        </div>
      )}
    </main>
  );
}
