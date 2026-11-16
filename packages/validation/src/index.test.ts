import { describe, expect, it } from "vitest";

import { validateRequiredText } from "./index";

describe("validateRequiredText", () => {
  it("trims valid text", () => {
    expect(validateRequiredText("title", "  hello ")).toEqual({
      value: "hello",
      issues: [],
      valid: true,
    });
  });

  it("rejects empty text", () => {
    const result = validateRequiredText("title", "   ");
    expect(result.valid).toBe(false);
    expect(result.issues).toEqual([{ field: "title", message: "This field is required." }]);
  });
});
