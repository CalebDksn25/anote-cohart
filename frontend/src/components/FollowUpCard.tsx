import { FollowUp } from "@/types/extraction";

interface Props {
  item: FollowUp;
}

export default function FollowUpCard({ item }: Props) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-gray-900">{item.text}</p>
        {item.needs_human_review && (
          <span className="shrink-0 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
            Needs review
          </span>
        )}
      </div>
      <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-600">
        {item.owner && (
          <>
            <dt className="font-medium">Owner</dt>
            <dd>{item.owner}</dd>
          </>
        )}
        {item.due && (
          <>
            <dt className="font-medium">Due</dt>
            <dd>{item.due}</dd>
          </>
        )}
        {item.due_raw && !item.due && (
          <>
            <dt className="font-medium">Due (raw)</dt>
            <dd>{item.due_raw}</dd>
          </>
        )}
        {item.reason && (
          <>
            <dt className="font-medium">Review reason</dt>
            <dd className="text-amber-700">{item.reason}</dd>
          </>
        )}
      </dl>
      <details className="mt-3">
        <summary className="cursor-pointer text-xs text-gray-400 hover:text-gray-600">
          Evidence
        </summary>
        <blockquote className="mt-1 border-l-2 border-gray-200 pl-3 text-xs italic text-gray-500">
          {item.evidence}
        </blockquote>
      </details>
    </div>
  );
}
