import { expect, describe, it } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import Home from "../../src/app/page";

describe("Home Page", async () => {
  const { container } = render(<Home />);

  it("should render new chat creation form", () => {
    waitFor(() => expect(screen.getByText("Start chat")).toBeInTheDocument());
    expect(screen.getByText("Start chat")).toBeInTheDocument();

    waitFor(() => {
      const newChatForm = container.querySelector("form");
      const newChatFormGroupInputs = newChatForm?.querySelectorAll("input");
      const newChatFormStartChatButton =
        newChatForm?.querySelectorAll("button");
      const newChatFormInputDetails = Array.from(
        newChatFormGroupInputs !== undefined &&
          newChatFormGroupInputs.length > 0
          ? newChatFormGroupInputs!.values()
          : []
      ).map((v) => v);

      expect(newChatForm).toBeDefined();
      expect(newChatFormGroupInputs?.length).toEqual(2);
      expect(
        newChatFormInputDetails.find(
          (e) =>
            e.id === "new-group-chat-name" &&
            e.type === "text" &&
            e.placeholder == "Group Chat name"
        )
      );
      expect(
        newChatFormInputDetails.find(
          (e) =>
            e.id === "new-group-chat-number-of-users" &&
            e.type === "number" &&
            e.placeholder == "Number of group chat users"
        )
      );
      expect(
        newChatFormInputDetails.find(
          (e) =>
            e.id === "new-group-chat-context" &&
            e.type === "text" &&
            e.placeholder ==
              "Chat Context - General topic, mood and sentiment of the group chat."
        )
      );
      expect(newChatFormStartChatButton?.length).toEqual(1);
      expect(newChatFormStartChatButton?.item(0).id).toEqual(
        "start-group-chat-btn"
      );
      expect(newChatFormStartChatButton?.item(0).type).toEqual("submit");
    });
  });
});
