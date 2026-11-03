export interface ValidationIssue {
  field: string;
  message: string;
}

export interface ValidationResult<T> {
  value?: T;
  issues: ValidationIssue[];
  valid: boolean;
}

export function validateRequiredText(field: string, value: string): ValidationResult<string> {
  const normalized = value.trim();

  if (normalized.length === 0) {
    return {
      issues: [{ field, message: "This field is required." }],
      valid: false,
    };
  }

  return { value: normalized, issues: [], valid: true };
}
