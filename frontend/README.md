# anote-cohart — Frontend

Next.js 15 web interface for uploading meeting transcripts and viewing structured extraction results.

## Setup

```bash
cd frontend
npm install
```

Create `.env.local` (already committed with defaults):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running

```bash
npm run dev
```

Open `http://localhost:3000`. The backend must be running at `NEXT_PUBLIC_API_URL` for uploads to work — see `api/README.md`.

## Usage

1. Drag and drop a `.txt` transcript onto the upload area, or click to browse.
2. Click **Extract**.
3. Results appear in a tabbed view — **Action Items**, **Decisions**, **Follow-ups** — with item counts on each tab.
4. Click **Evidence** under any card to expand the source quote from the transcript.
5. Items flagged for human review show an amber **Needs review** badge with a reason.
6. If the transcript is missing a `Date:` header or is very short, an amber warning banner appears above the results.
7. Validation errors (empty file, no speaker lines, etc.) appear inline as a red alert.

## Layout

```
src/
├── app/
│   ├── layout.tsx           Root layout, metadata
│   ├── page.tsx             Main page — discriminated union state machine
│   └── globals.css          Tailwind base styles
├── components/
│   ├── UploadForm.tsx        Drag-and-drop .txt file picker
│   ├── ResultsPanel.tsx      Tabbed results view
│   ├── ActionItemCard.tsx    Owner, due date, review badge, evidence
│   ├── DecisionCard.tsx      Text and evidence
│   ├── FollowUpCard.tsx      Owner, due date, review badge, evidence
│   ├── ValidationBanner.tsx  Amber banner for soft warnings
│   ├── ErrorAlert.tsx        Red alert with optional validation error list
│   └── LoadingSpinner.tsx    Animated spinner shown during extraction
├── lib/
│   └── api.ts               fetch wrapper — extractTranscript(), ExtractionApiError
└── types/
    └── extraction.ts         TypeScript interfaces mirroring backend Pydantic models
```

## State machine

The page uses a discriminated union to prevent impossible UI states:

```typescript
type AppState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ExtractionResponse }
  | { status: "error"; message: string; validationErrors?: string[] }
```

## API error handling

`ExtractionApiError` captures the HTTP status code and structured detail from the backend:

- **422** with `{ message, errors, warnings }` → renders the `errors` list in `ErrorAlert`
- **401** → shows auth error message
- **502** → shows upstream LLM failure message
- Network errors → shows the raw error message
