import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Chat from "../../../src/app/chat/[chat_uuid]/page";

describe("Chat Page Initial Load", () => {
  it("Asserts chat page loads chat with correct chat title supplied in chat creation form", async () => {
    render(<Chat params={{ chat_uuid: crypto.randomUUID() }} />);

    await waitFor(() => {
      expect(screen.getByText("Hello world")).toBeInTheDocument();
    });
  });
});
