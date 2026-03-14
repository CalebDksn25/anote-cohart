export interface TranscriptValidationResult {
  valid: boolean;
  warnings: string[];
  errors: string[];
}

export interface ActionItem {
  text: string;
  owner: string | null;
  due_raw: string | null;
  due: string | null;
  evidence: string;
  needs_human_review: boolean;
  reason: string | null;
}

export interface Decision {
  text: string;
  evidence: string;
}

export interface FollowUp {
  text: string;
  owner: string | null;
  due_raw: string | null;
  due: string | null;
  evidence: string;
  needs_human_review?: boolean | null;
  reason?: string | null;
}

export interface ExtractionResponse {
  action_items: ActionItem[];
  decisions: Decision[];
  follow_ups: FollowUp[];
  validation: TranscriptValidationResult;
}

export interface ValidationErrorDetail {
  message: string;
  errors: string[];
  warnings: string[];
}
