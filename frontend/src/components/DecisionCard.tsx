import { Decision } from "@/types/extraction";

interface Props {
  item: Decision;
}

export default function DecisionCard({ item }: Props) {
  return (
    <div className="rounded-xl border border-[#1e3a5f] bg-[#0f1e35] p-4 transition-colors hover:border-cyan-500/30">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 shrink-0 rounded-full border border-cyan-500/30 bg-cyan-500/10 p-1">
          <svg className="h-3 w-3 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </span>
        <p className="font-medium text-white">{item.text}</p>
      </div>

      <details className="mt-3 group ml-7">
        <summary className="cursor-pointer list-none text-xs text-slate-600 transition-colors hover:text-slate-400 group-open:text-slate-400">
          <span className="group-open:hidden">▸ Evidence</span>
          <span className="hidden group-open:inline">▾ Evidence</span>
        </summary>
        <blockquote className="mt-2 border-l-2 border-cyan-500/30 pl-3 text-xs italic text-slate-500">
          {item.evidence}
        </blockquote>
      </details>
    </div>
  );
}
