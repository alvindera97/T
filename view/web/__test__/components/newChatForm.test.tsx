import { HTMLInputTypeAttribute } from "react";
import userEvent from "@testing-library/user-event";
import { executeRandomCallable } from "../../src/utils";
import NewChatForm from "../../src/components/NewChatForm";
import { render, screen, waitFor } from "@testing-library/react";
import { expect, describe, it, beforeEach, afterEach } from "vitest";

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

  it("Asserts new chat form method is POST", () => {
    expect(formElement.getAttribute("method")).toEqual("POST");
  });

  it("Asserts new chat form action is set to appropriate url", () => {
    expect(formElement.getAttribute("action")).toEqual(
      `${process.env.NEXT_PUBLIC_T_BACKEND_URL}/set_up_chat/`
    );
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
  const { container } = render(<NewChatForm />);
  const newGroupChatForm = container.querySelectorAll("form");
  const groupChatNameInput = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-name");

  it("Asserts group chat name input is child of child element of single form element", () => {
    expect(newGroupChatForm.length).toEqual(1);
    expect(groupChatNameInput).toBeInTheDocument();
  });

  it("Asserts group chat name input is enabled", () => {
    expect(groupChatNameInput).toBeEnabled();
  });

  it("Asserts group chat name input is editable", async () => {
    if (groupChatNameInput === null) {
      fail("Input for group chat name wasn't found!");
    }

    // https://github.com/testing-library/user-event/issues/1150#issuecomment-1851795697
    await userEvent.type(groupChatNameInput, "Hello world");

    expect(groupChatNameInput).toHaveValue("Hello world");
  });
});

describe("Assert <NewChatForm /> Group Chat Context Input Details", () => {
  const { container } = render(<NewChatForm />);
  const newGroupChatForm = container.querySelectorAll("form");
  const groupChatContextInput = newGroupChatForm
    .item(0)
    .querySelector("textarea#new-group-chat-context");

  if (groupChatContextInput === null) {
    fail("Input for group chat context wasn't found");
  }

  it("Asserts group chat group context input is child of child element of single form element", () => {
    expect(newGroupChatForm.length).toEqual(1);
    expect(groupChatContextInput).toBeInTheDocument();
  });

  it("Asserts group chat group context input is enabled", () => {
    expect(groupChatContextInput).toBeEnabled();
  });

  it("Asserts group chat group context input is editable", async () => {
    await userEvent.type(
      groupChatContextInput,
      "Hello world, this is the group chat context"
    );

    expect(groupChatContextInput).toHaveValue(
      "Hello world, this is the group chat context"
    );
  });
});

describe("Assert <NewChatForm /> Number Of Chat users Input Details", () => {
  const { container } = render(<NewChatForm />);
  const newGroupChatForm = container.querySelectorAll("form");
  const groupChatNumberOfUsersInput = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-number-of-users");

  if (groupChatNumberOfUsersInput === null) {
    fail("Input for group chat number of users wasn't found");
  }

  it("Asserts group chat number of users input is child of child element of single form element", () => {
    expect(newGroupChatForm.length).toEqual(1);
    expect(groupChatNumberOfUsersInput).toBeInTheDocument();
  });

  it("Asserts group chat group number of users input is enabled ", () => {
    expect(groupChatNumberOfUsersInput).toBeEnabled();
  });

  it("Asserts group chat group number of users input is editable", async () => {
    await userEvent.type(groupChatNumberOfUsersInput, "10");

    expect(groupChatNumberOfUsersInput).toHaveValue(10);
  });

  it("Asserts group chat number of users input only accepts positive integer Number inputs", async () => {
    await userEvent.clear(groupChatNumberOfUsersInput);
    await userEvent.type(groupChatNumberOfUsersInput, "string input");

    expect(groupChatNumberOfUsersInput).toBeEmptyDOMElement();
  });

  it("Asserts group chat number of users input cannot accept any value below 1", async () => {
    await userEvent.clear(groupChatNumberOfUsersInput);
    await userEvent.type(groupChatNumberOfUsersInput, "0");

    expect(groupChatNumberOfUsersInput).toBeEmptyDOMElement();
  });
});

describe("Assert <NewChatForm /> Start Chat (Submit) Button Details", () => {
  const { container } = render(<NewChatForm />);
  const queryResultLength = container.querySelectorAll(
    "button#start-group-chat-btn"
  ).length;

  if (queryResultLength !== 1) {
    fail(
      `Expected to find 1 element in query result for 'start chat button', found: ${queryResultLength}`
    );
  }

  const startChatButton = container.querySelector(
    "button#start-group-chat-btn"
  )!;

  const newGroupChatForm = container.querySelectorAll("form");
  const groupChatNameInput = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-name");
  const groupChatContextInput = newGroupChatForm
    .item(0)
    .querySelector("textarea#new-group-chat-context");
  const groupChatNumberOfUsersInput = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-number-of-users");

  it("Asserts the submit button is disabled at first render of the component", () => {
    expect(startChatButton).toBeDisabled();
  });

  if (
    groupChatNameInput === null ||
    groupChatContextInput === null ||
    groupChatNumberOfUsersInput === null
  ) {
    fail("Failed to find all inputs for the 'start group chat' form.");
  }

  beforeEach(() => {
    userEvent.clear(groupChatNameInput);
    userEvent.clear(groupChatContextInput);
    userEvent.clear(groupChatNumberOfUsersInput);
  });

  afterEach(() => {
    userEvent.clear(groupChatNameInput);
    userEvent.clear(groupChatContextInput);
    userEvent.clear(groupChatNumberOfUsersInput);
  });

  it("Asserts the submit button is disabled when only the group chat name is entered", async () => {
    await userEvent.type(groupChatNameInput, "hello world");

    expect(startChatButton).toBeDisabled();
  });

  it("Asserts the submit button is disabled when only the group chat context is entered", async () => {
    await userEvent.type(groupChatContextInput, "group chat context");

    expect(startChatButton).toBeDisabled();
  });

  it("Asserts the submit button is disabled when only the group chat number of users is entered", async () => {
    await userEvent.type(groupChatNumberOfUsersInput, "10");

    expect(startChatButton).toBeDisabled();
  });

  it("Asserts the submit button is disabled when all the inputs have not been filled", async () => {
    await executeRandomCallable(
      [
        [async () => await userEvent.type(groupChatNameInput, "hello world")],
        [async () => await userEvent.type(groupChatNumberOfUsersInput, "10")],
        [
          async () =>
            await userEvent.type(groupChatContextInput, "group chat context"),
        ],
      ],
      2
    );

    expect(startChatButton).toBeDisabled();
  });

  it("Assert that the submit button is enabled after all form inputs are entered", async () => {
    await executeRandomCallable(
      [
        [async () => await userEvent.type(groupChatNameInput, "hello world")],
        [async () => await userEvent.type(groupChatNumberOfUsersInput, "10")],
        [
          async () =>
            await userEvent.type(groupChatContextInput, "group chat context"),
        ],
      ],
      3
    );

    expect(startChatButton).toBeEnabled();
  });

  it("Asserts that the submit button is disabled once it is clicked", async () => {
    await executeRandomCallable(
      [
        [async () => await userEvent.type(groupChatNameInput, "hello world")],
        [async () => await userEvent.type(groupChatNumberOfUsersInput, "10")],
        [
          async () =>
            await userEvent.type(groupChatContextInput, "group chat context"),
        ],
      ],
      3
    );

    expect(startChatButton).toBeEnabled();
    await userEvent.click(startChatButton);
    expect(startChatButton).toBeDisabled();
  });
});
