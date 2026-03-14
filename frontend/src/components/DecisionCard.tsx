import { Decision } from "@/types/extraction";

interface Props {
  item: Decision;
}

export default function DecisionCard({ item }: Props) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <p className="font-medium text-gray-900">{item.text}</p>
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
