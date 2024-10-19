import { expect, describe, it } from "vitest";
import { render, screen } from "@testing-library/react";
import NewChatForm from "../../src/components/NewChatForm";
import { HTMLInputTypeAttribute } from "react";

// Asserts new chat form component renders expected components

describe("Assert <NewChatForm /> Contents", () => {
  const { container } = render(<NewChatForm />);
  const formElement: HTMLInputElement = screen.getByRole("start-new-chat-form");

  it("Assert new chat form role is of start-new-chat-form and it renders.", () => {
    expect(formElement).toBeInTheDocument();
  });

  it("Asserts new chat from is an HTMLFormElement", () => {
    expect(formElement).toBeInstanceOf(HTMLFormElement);
  });

  it("Asserts new chat form is ID new-chat-form", () => {
    expect(formElement.id).toEqual("new-chat-form");
  });

  it("Asserts new chat form action is POST", () => {
    expect(formElement.getAttribute("action")).toEqual("POST");
  });

  it("Asserts there is a singular form element in the component", () => {
    const element = container.querySelectorAll("form");

    expect(element.length).toEqual(1);
    expect(element.item(0).id).toEqual("new-chat-form");
    expect(element.item(0).role).toEqual("start-new-chat-form");
  });

  it("Asserts new new chat form contains input for group chat name", () => {
    const elements: Array<{
      id: string;
      placeholder: string;
      type: HTMLInputTypeAttribute;
    }> = new Array();

    container.querySelectorAll("input").forEach((element) =>
      elements.push({
        id: element.id,
        type: element.type,
        placeholder: element.placeholder,
      })
    );

    expect(elements.length).toBeGreaterThan(0);
    expect(
      elements.find(
        (element) =>
          element.id === "new-group-chat-name" &&
          element.placeholder === "Group chat name" &&
          element.type === "text"
      )
    ).toBeTruthy();
  });

  it("Asserts new chat form contains input for chat context", () => {
    const elements: Array<{
      id: string;
      placeholder: string;
    }> = new Array();

    container.querySelectorAll("textarea").forEach((element) =>
      elements.push({
        id: element.id,
        placeholder: element.placeholder,
      })
    );

    expect(elements.length).toBeGreaterThan(0);
    expect(
      elements.find(
        (element) =>
          element.id === "new-group-chat-context" &&
          element.placeholder ===
            "Chat context — General topic, mood and sentiment of the group chat."
      )
    ).toBeTruthy();
  });

  it("Assert new chat form contains input for number of chat members", () => {
    const elements: Array<{
      id: string;
      placeholder: string;
      type: HTMLInputTypeAttribute;
    }> = new Array();

    container.querySelectorAll("input").forEach((element) =>
      elements.push({
        id: element.id,
        type: element.type,
        placeholder: element.placeholder,
      })
    );

    expect(elements.length).toBeGreaterThan(0);
    expect(
      elements.find(
        (element) =>
          element.id === "new-group-chat-number-of-users" &&
          element.placeholder === "Number of group chat users" &&
          element.type === "number"
      )
    ).toBeTruthy();
  });

  it("Asserts new chat form contains button to start chat (submit button)", () => {
    const querySelectorElements = container.querySelectorAll("button");

    const elements: Array<{
      id: string;
      type: HTMLInputTypeAttribute;
    }> = new Array();

    querySelectorElements.forEach((element) =>
      elements.push({
        id: element.id,
        type: element.type,
      })
    );

    expect(elements.length).toEqual(1);
    expect(querySelectorElements.item(0).textContent).equals("Start chat");
    expect(
      elements.find(
        (element) =>
          element.id === "start-group-chat-btn" && element.type === "submit"
      )
    ).toBeTruthy();
  });
});

describe("Assert <NewChatForm /> Group Chat Name Input Details", () => {
  render(<NewChatForm />);

  it("Asserts group name chat input is child of child element of single form element", () => {});
});

describe("Assert <NewChatForm /> Group Chat Context Input Details", () => {
  render(<NewChatForm />);

  it("", () => {});
});

describe("Assert <NewChatForm /> Number Of Chat Members Input Details", () => {
  render(<NewChatForm />);

  it("", () => {});
});

describe("Assert <NewChatForm /> Start Chat (Submit) Button Details", () => {
  render(<NewChatForm />);

  it("", () => {});
});
