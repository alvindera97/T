import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Chat from "../../../src/app/chat/[chat_uuid]/page";

describe("Chat Page", () => {
  describe("on load", () => {
    describe("renders the chat page ", () => {
      it("with details associated with the chat UUID", async () => {
        render(<Chat params={{ chat_uuid: crypto.randomUUID() }} />);

        await waitFor(() => {
          expect(screen.getByText("Hello world")).toBeInTheDocument();
        });
      });
    });
  });
});
