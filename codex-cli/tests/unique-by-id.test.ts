import { describe, test, expect } from "vitest";
import { uniqueById } from "../src/utils/model-utils";

function assistant(id: string) {
  return {
    id,
    type: "message",
    role: "assistant",
    content: [],
  } as any;
}

function user(text: string) {
  return {
    type: "message",
    role: "user",
    content: [{ type: "input_text", text }],
  } as any;
}

describe("uniqueById", () => {
  test("de-duplicates items with the same id", () => {
    const a1 = assistant("a");
    const b = assistant("b");
    const a2 = assistant("a");

    const result = uniqueById([a1, b, a2]);

    expect(result).toHaveLength(2);
    expect(result[0]).toBe(a1);
    expect(result[1]).toBe(b);
  });

  test("collapses consecutive identical user messages", () => {
    const u1 = user("hi");
    const u2 = user("hi");
    const asst = assistant("x");
    const u3 = user("hi");

    const result = uniqueById([u1, u2, asst, u3]);

    expect(result).toHaveLength(3);
    expect(result[0]).toBe(u1);
    expect(result[1]).toBe(asst);
    expect(result[2]).toBe(u3);
  });
});
