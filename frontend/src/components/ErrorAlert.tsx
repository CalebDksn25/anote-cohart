import { ValidationErrorDetail } from "@/types/extraction";

interface Props {
  message: string;
  validationErrors?: string[];
}

export default function ErrorAlert({ message, validationErrors }: Props) {
  return (
    <div className="rounded-lg border border-red-300 bg-red-50 p-4">
      <h3 className="font-medium text-red-800">{message}</h3>
      {validationErrors && validationErrors.length > 0 && (
        <ul className="mt-2 list-inside list-disc space-y-0.5 text-sm text-red-700">
          {validationErrors.map((e, i) => (
            <li key={i}>{e}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
