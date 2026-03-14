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

      <div className="flex gap-1 rounded-lg border border-gray-200 bg-gray-100 p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={[
              "flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              activeTab === tab.id
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-500 hover:text-gray-700",
            ].join(" ")}
          >
            {tab.label}
            <span
              className={[
                "rounded-full px-1.5 py-0.5 text-xs",
                activeTab === tab.id
                  ? "bg-blue-100 text-blue-700"
                  : "bg-gray-200 text-gray-500",
              ].join(" ")}
            >
              {counts[tab.id]}
            </span>
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {activeTab === "action_items" &&
          (data.action_items.length === 0 ? (
            <p className="py-8 text-center text-sm text-gray-400">
              No action items found.
            </p>
          ) : (
            data.action_items.map((item, i) => (
              <ActionItemCard key={i} item={item} />
            ))
          ))}

        {activeTab === "decisions" &&
          (data.decisions.length === 0 ? (
            <p className="py-8 text-center text-sm text-gray-400">
              No decisions found.
            </p>
          ) : (
            data.decisions.map((item, i) => (
              <DecisionCard key={i} item={item} />
            ))
          ))}

        {activeTab === "follow_ups" &&
          (data.follow_ups.length === 0 ? (
            <p className="py-8 text-center text-sm text-gray-400">
              No follow-ups found.
            </p>
          ) : (
            data.follow_ups.map((item, i) => (
              <FollowUpCard key={i} item={item} />
            ))
          ))}
      </div>
    </div>
  );
}
