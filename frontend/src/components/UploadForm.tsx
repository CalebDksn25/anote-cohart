"use client";

import { useCallback, useRef, useState } from "react";

interface Props {
  onSubmit: (file: File) => void;
  disabled?: boolean;
}

export default function UploadForm({ onSubmit, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = useCallback((file: File) => {
    setSelectedFile(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFile) onSubmit(selectedFile);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div
        onClick={() => !disabled && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={[
          "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-all",
          dragOver
            ? "border-cyan-400 bg-cyan-400/5 glow-cyan"
            : "border-[#1e3a5f] bg-[#0a1628] hover:border-cyan-500/40 hover:bg-cyan-400/5",
          disabled ? "cursor-not-allowed opacity-40" : "",
        ].join(" ")}
      >
        {/* Upload icon */}
        <svg
          className={`mb-4 h-10 w-10 transition-colors ${dragOver ? "text-cyan-400" : "text-slate-600"}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
          />
        </svg>
        {selectedFile ? (
          <div className="flex items-center gap-2">
            <svg className="h-4 w-4 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
            <p className="text-sm font-medium text-cyan-400">{selectedFile.name}</p>
          </div>
        ) : (
          <>
            <p className="text-sm font-medium text-slate-300">
              Drag & drop your transcript here
            </p>
            <p className="mt-1 text-xs text-slate-500">
              or <span className="text-cyan-400">click to browse</span> — .txt files only
            </p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".txt,text/plain"
          className="hidden"
          onChange={handleChange}
          disabled={disabled}
        />
      </div>
      <button
        type="submit"
        disabled={!selectedFile || disabled}
        className="w-full rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-[#0a1628] transition-all hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Extract
      </button>
    </form>
  );
}
