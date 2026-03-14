"use client";

import { useState } from "react";
import { ExtractionResponse } from "@/types/extraction";
import ActionItemCard from "./ActionItemCard";
import DecisionCard from "./DecisionCard";
import FollowUpCard from "./FollowUpCard";
import ValidationBanner from "./ValidationBanner";

interface Props {
  data: ExtractionResponse;
}

type Tab = "action_items" | "decisions" | "follow_ups";

const TABS: { id: Tab; label: string }[] = [
  { id: "action_items", label: "Action Items" },
  { id: "decisions", label: "Decisions" },
  { id: "follow_ups", label: "Follow-ups" },
];

export default function ResultsPanel({ data }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>("action_items");

  const counts = {
    action_items: data.action_items.length,
    decisions: data.decisions.length,
    follow_ups: data.follow_ups.length,
  };

  return (
    <div className="space-y-4">
      {data.validation.warnings.length > 0 && (
        <ValidationBanner warnings={data.validation.warnings} />
      )}

      {/* Tab bar */}
      <div className="flex gap-1 rounded-xl border border-[#1e3a5f] bg-[#0f1e35] p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={[
              "flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all",
              activeTab === tab.id
                ? "bg-[#0a1628] text-white shadow-sm border border-[#1e3a5f]"
                : "text-slate-500 hover:text-slate-300",
            ].join(" ")}
          >
            {tab.label}
            <span
              className={[
                "rounded-full px-1.5 py-0.5 text-xs font-semibold",
                activeTab === tab.id
                  ? "bg-cyan-500/20 text-cyan-400"
                  : "bg-slate-700/50 text-slate-500",
              ].join(" ")}
            >
              {counts[tab.id]}
            </span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="space-y-3">
        {activeTab === "action_items" &&
          (data.action_items.length === 0 ? (
            <EmptyState label="No action items found." />
          ) : (
            data.action_items.map((item, i) => (
              <ActionItemCard key={i} item={item} />
            ))
          ))}

        {activeTab === "decisions" &&
          (data.decisions.length === 0 ? (
            <EmptyState label="No decisions found." />
          ) : (
            data.decisions.map((item, i) => <DecisionCard key={i} item={item} />)
          ))}

        {activeTab === "follow_ups" &&
          (data.follow_ups.length === 0 ? (
            <EmptyState label="No follow-ups found." />
          ) : (
            data.follow_ups.map((item, i) => (
              <FollowUpCard key={i} item={item} />
            ))
          ))}
      </div>
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <p className="py-10 text-center text-sm text-slate-600">{label}</p>
  );
}
