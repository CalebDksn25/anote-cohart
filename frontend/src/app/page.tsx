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
      {/* Top nav bar */}
      <nav className="border-b border-[#1e3a5f] px-6 py-4">
        <div className="mx-auto flex max-w-3xl items-center gap-2">
          {/* Anote logo mark — stylised rocket pen */}
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none" aria-hidden>
            <path
              d="M4 18L9.5 12.5M9.5 12.5L14 4L18 8L9.5 12.5Z"
              stroke="#22d3ee"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="4.5" cy="17.5" r="1.5" fill="#22d3ee" />
          </svg>
          <span className="text-lg font-semibold tracking-tight text-white">
            Anote
          </span>
          <span className="ml-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 text-[11px] font-medium text-cyan-400">
            Cohart
          </span>
        </div>
      </nav>

      <div className="mx-auto max-w-3xl px-4 py-12">
        {/* Hero */}
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-white">
            Meeting Transcript Extractor
          </h1>
          <p className="mt-3 text-base" style={{ color: "var(--muted)" }}>
            Upload a transcript and instantly surface action items, decisions,
            and follow-ups — powered by{" "}
            <span className="text-cyan-400">Human Centered AI</span>.
          </p>
        </header>

        {/* Upload card */}
        {state.status !== "success" && (
          <div
            className="rounded-2xl border p-6"
            style={{
              background: "var(--card)",
              borderColor: "var(--card-border)",
            }}
          >
            <UploadForm
              onSubmit={handleSubmit}
              disabled={state.status === "loading"}
            />
          </div>
        )}

        <div className="mt-6 space-y-4">
          {state.status === "loading" && <LoadingSpinner />}

          {state.status === "error" && (
            <>
              <ErrorAlert
                message={state.message}
                validationErrors={state.validationErrors}
              />
              <button
                onClick={handleReset}
                className="w-full rounded-lg border border-[#1e3a5f] bg-[#0f1e35] px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:border-cyan-500/50 hover:text-white"
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
                className="w-full rounded-lg border border-[#1e3a5f] bg-[#0f1e35] px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:border-cyan-500/50 hover:text-white"
              >
                Upload another transcript
              </button>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
