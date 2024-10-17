import { expect, describe, it } from "vitest";
import { render, screen } from "@testing-library/react";
import NewChatForm from "../../src/components/NewChatForm";

// Asserts new chat form component renders expected components

describe("Assert <NewChatForm /> Contents", () => {
  render(<NewChatForm />);
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
});
