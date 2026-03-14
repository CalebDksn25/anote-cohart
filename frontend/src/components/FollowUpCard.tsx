import { FollowUp } from "@/types/extraction";

interface Props {
  item: FollowUp;
}

export default function FollowUpCard({ item }: Props) {
  return (
    <div className="rounded-xl border border-[#1e3a5f] bg-[#0f1e35] p-4 transition-colors hover:border-cyan-500/30">
      <div className="flex items-start justify-between gap-3">
        <p className="font-medium text-white">{item.text}</p>
        {item.needs_human_review && (
          <span className="shrink-0 rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-400">
            Needs review
          </span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-3">
        {item.owner && (
          <Chip icon="👤" label={item.owner} />
        )}
        {item.due && (
          <Chip icon="📅" label={item.due} highlight />
        )}
        {item.due_raw && !item.due && (
          <Chip icon="📅" label={item.due_raw} />
        )}
      </div>

      {item.reason && (
        <p className="mt-2 text-xs text-amber-400/80">{item.reason}</p>
      )}

      <details className="mt-3 group">
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

function Chip({
  icon,
  label,
  highlight,
}: {
  icon: string;
  label: string;
  highlight?: boolean;
}) {
  return (
    <span
      className={[
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        highlight
          ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
          : "border-[#1e3a5f] bg-[#0a1628] text-slate-400",
      ].join(" ")}
    >
      {icon} {label}
    </span>
  );
}
