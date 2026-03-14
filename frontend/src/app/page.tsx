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
    <main className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-2xl px-4 py-12">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            anote
          </h1>
          <p className="mt-2 text-gray-500">
            Upload a meeting transcript to extract action items, decisions, and
            follow-ups.
          </p>
        </header>

        {state.status !== "success" && (
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <UploadForm
              onSubmit={handleSubmit}
              disabled={state.status === "loading"}
            />
          </div>
        )}

        <div className="mt-6">
          {state.status === "loading" && <LoadingSpinner />}

          {state.status === "error" && (
            <div className="space-y-4">
              <ErrorAlert
                message={state.message}
                validationErrors={state.validationErrors}
              />
              <button
                onClick={handleReset}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                Try again
              </button>
            </div>
          )}

          {state.status === "success" && (
            <div className="space-y-4">
              <ResultsPanel data={state.data} />
              <button
                onClick={handleReset}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                Upload another transcript
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
