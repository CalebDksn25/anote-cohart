interface Props {
  warnings: string[];
}

export default function ValidationBanner({ warnings }: Props) {
  if (!warnings.length) return null;
  return (
    <div className="rounded-lg border border-amber-300 bg-amber-50 p-4">
      <h3 className="mb-1 font-medium text-amber-800">Transcript warnings</h3>
      <ul className="list-inside list-disc space-y-0.5 text-sm text-amber-700">
        {warnings.map((w, i) => (
          <li key={i}>{w}</li>
        ))}
      </ul>
    </div>
  );
}
