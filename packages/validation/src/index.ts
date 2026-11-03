/** Client-side validators mirroring API rules. The API remains the authority; these only improve feedback. */
export const PASSWORD_MIN_LENGTH = 12;

export function validateEmail(value: string): string | null {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim()) ? null : "Enter a valid email address.";
}

export function validatePassword(value: string): string | null {
  return value.length >= PASSWORD_MIN_LENGTH ? null : `Use at least ${PASSWORD_MIN_LENGTH} characters.`;
}

export function validateHttpUrl(value: string): string | null {
  if (!value.trim()) return null;
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:" ? null : "Only http(s) links are allowed.";
  } catch {
    return "Enter a valid URL.";
  }
}

export function required(value: string, label: string, min = 1): string | null {
  return value.trim().length >= min ? null : `${label} must be at least ${min} character${min === 1 ? "" : "s"}.`;
}

export function firstError(...errors: Array<string | null>): string | null {
  return errors.find((error) => error !== null) ?? null;
}
