export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <div className="relative h-10 w-10">
        <div className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-cyan-400" />
        <div className="absolute inset-1 animate-spin rounded-full border-2 border-transparent border-t-cyan-600 [animation-duration:1.5s]" />
      </div>
      <p className="text-sm text-slate-500">Extracting transcript…</p>
    </div>
  );
}
