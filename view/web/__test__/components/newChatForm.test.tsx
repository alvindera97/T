import { HTMLInputTypeAttribute } from "react";
import userEvent from "@testing-library/user-event";
import { executeRandomCallable } from "../../src/utils";
import NewChatForm from "../../src/components/NewChatForm";
import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import axios from "axios";
import { Toaster, toast } from "react-hot-toast";

// Asserts new chat form component renders expected components

describe("<NewChatForm /> component", () => {
  const { container } = render(<NewChatForm />);
  const formElement: HTMLInputElement = screen.getByRole("start-new-chat-form");

  it("form role is of start-new-chat-form.", () => {
    expect(formElement).toBeInTheDocument();
  });

  it("form is an HTMLFormElement", () => {
    expect(formElement).toBeInstanceOf(HTMLFormElement);
  });

  it("form is ID new-chat-form", () => {
    expect(formElement.id).toEqual("new-chat-form");
  });

  it("contains a singular form element in the component", () => {
    const element = container.querySelectorAll("form");

    expect(element.length).toEqual(1);
    expect(element.item(0).id).toEqual("new-chat-form");
    expect(element.item(0).role).toEqual("start-new-chat-form");
  });

  it("contains input for group chat name", () => {
    const elements: Array<{
      id: string;
      placeholder: string;
      type: HTMLInputTypeAttribute;
    }> = [];

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

  it("contains input for chat context", () => {
    const elements: Array<{
      id: string;
      placeholder: string;
    }> = [];

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

  it("contains input for number of chat members", () => {
    const elements: Array<{
      id: string;
      placeholder: string;
      type: HTMLInputTypeAttribute;
    }> = [];

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

  it("contains button to start chat (submit button)", () => {
    const querySelectorElements = container.querySelectorAll("button");

    const elements: Array<{
      id: string;
      type: HTMLInputTypeAttribute;
    }> = [];

    querySelectorElements.forEach((element) =>
      elements.push({
        id: element.id,
        type: element.type,
      })
    );

    expect(elements.length).toEqual(1);
    expect(querySelectorElements.item(0).textContent).equals("Start chat");
  });
});

describe("<NewChatForm /> component group chat name input", () => {
  const { container } = render(<NewChatForm />);
  const newGroupChatForm = container.querySelectorAll("form");
  const groupChatNameInput = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-name");

  it("is child of child element of single form element", () => {
    expect(newGroupChatForm.length).toEqual(1);
    expect(groupChatNameInput).toBeInTheDocument();
  });

  it("is enabled", () => {
    expect(groupChatNameInput).toBeEnabled();
  });

  it("is editable", async () => {
    if (groupChatNameInput === null) {
      fail("Input for group chat name wasn't found!");
    }

    // https://github.com/testing-library/user-event/issues/1150#issuecomment-1851795697
    await userEvent.type(groupChatNameInput, "Hello world");

    expect(groupChatNameInput).toHaveValue("Hello world");
  });
});

describe("<NewChatForm /> component group chat context input", () => {
  const { container } = render(<NewChatForm />);
  const newGroupChatForm = container.querySelectorAll("form");
  const groupChatContextInput = newGroupChatForm
    .item(0)
    .querySelector("textarea#new-group-chat-context");

  if (groupChatContextInput === null) {
    fail("Input for group chat context wasn't found");
  }

  it("is child of child element of single form element", () => {
    expect(newGroupChatForm.length).toEqual(1);
    expect(groupChatContextInput).toBeInTheDocument();
  });

  it("is enabled", () => {
    expect(groupChatContextInput).toBeEnabled();
  });

  it("is editable", async () => {
    await userEvent.type(
      groupChatContextInput,
      "Hello world, this is the group chat context"
    );

    expect(groupChatContextInput).toHaveValue(
      "Hello world, this is the group chat context"
    );
  });
});

describe("<NewChatForm /> component number of chat users input", () => {
  const { container } = render(<NewChatForm />);
  const newGroupChatForm = container.querySelectorAll("form");
  const groupChatNumberOfUsersInput = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-number-of-users");

  if (groupChatNumberOfUsersInput === null) {
    fail("Input for group chat number of users wasn't found");
  }

  it("is child of child element of single form element", () => {
    expect(newGroupChatForm.length).toEqual(1);
    expect(groupChatNumberOfUsersInput).toBeInTheDocument();
  });

  it("is enabled ", () => {
    expect(groupChatNumberOfUsersInput).toBeEnabled();
  });

  it("is editable", async () => {
    await userEvent.type(groupChatNumberOfUsersInput, "10");

    expect(groupChatNumberOfUsersInput).toHaveValue(10);
  });

  it("only accepts positive integer number inputs", async () => {
    await userEvent.clear(groupChatNumberOfUsersInput);
    await userEvent.type(groupChatNumberOfUsersInput, "string input");

    expect(groupChatNumberOfUsersInput).toBeEmptyDOMElement();
  });

  it("cannot accept any value below 1", async () => {
    await userEvent.clear(groupChatNumberOfUsersInput);
    await userEvent.type(groupChatNumberOfUsersInput, "0");

    expect(groupChatNumberOfUsersInput).toBeEmptyDOMElement();
  });
});

describe("<NewChatForm /> component submit button", () => {
  const { container } = render(<NewChatForm />);
  render(<Toaster />);
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
  const groupChatNameInput: HTMLInputElement | null = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-name");
  const groupChatContextInput: HTMLTextAreaElement | null = newGroupChatForm
    .item(0)
    .querySelector("textarea#new-group-chat-context");
  const groupChatNumberOfUsersInput: HTMLInputElement | null = newGroupChatForm
    .item(0)
    .querySelector("input#new-group-chat-number-of-users");

  it("is disabled at first render of the component", () => {
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

    // Restore mocks
    vi.clearAllMocks();
  });

  /**
   * Randomly fill chat inputs
   *
   * @param numberOfInputsToFill number of inputs to fill.
   */
  async function randomlyFillNewChatFormInputs(numberOfInputsToFill: number) {
    await executeRandomCallable(
      [
        [async () => await userEvent.type(groupChatNameInput!, "hello world")],
        [async () => await userEvent.type(groupChatNumberOfUsersInput!, "10")],
        [
          async () =>
            await userEvent.type(groupChatContextInput!, "group chat context"),
        ],
      ],
      numberOfInputsToFill
    );
  }

  it("is disabled when only the group chat name is entered", async () => {
    await userEvent.type(groupChatNameInput, "hello world");

    expect(startChatButton).toBeDisabled();
  });

  it("is disabled when only the group chat context is entered", async () => {
    await userEvent.type(groupChatContextInput, "group chat context");

    expect(startChatButton).toBeDisabled();
  });

  it("is disabled when only the group chat number of users is entered", async () => {
    await userEvent.type(groupChatNumberOfUsersInput, "10");

    expect(startChatButton).toBeDisabled();
  });

  it("is disabled when all the inputs have not been filled", async () => {
    await randomlyFillNewChatFormInputs(2);

    expect(startChatButton).toBeDisabled();
  });

  it("is enabled after all form inputs are entered", async () => {
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

  it("is disabled once it is clicked", async () => {
    vi.mock("axios", () => ({
      default: {
        post: vi.fn().mockResolvedValue({ data: { success: true } }),
      },
    }));

    await randomlyFillNewChatFormInputs(3);

    expect(startChatButton).toBeEnabled();
    await userEvent.click(startChatButton);
    expect(startChatButton).toBeDisabled();
  });

  it("on failed axios request to start new chat, a toast indicating an error in setting up the chat is rendered for 7 seconds", async () => {
    vi.mock("axios", () => ({
      default: {
        post: vi.fn().mockRejectedValue(new Error("Connection Failed")),
      },
    }));

    // @ts-ignore
    vi.mock(import("react-hot-toast"), async (importOriginal) => {
      const actual = await importOriginal();
      return {
        ...actual,
        toast: {
          error: vi.fn(),
        },
      };
    });

    await randomlyFillNewChatFormInputs(3);
    await userEvent.click(startChatButton);

    expect(axios.post).toHaveBeenCalledOnce();

    await waitFor(
      () => {
        expect(toast.error).toHaveBeenCalledWith(
          <p>
            {process.env.NEXT_PUBLIC_CHAT_CREATION_FAILURE_MESSAGE !== undefined
              ? process.env.NEXT_PUBLIC_CHAT_CREATION_FAILURE_MESSAGE
              : "An error occurred while setting up your chat"}
          </p>,
          {
            duration: 7000,
          }
        );
      },
      { timeout: 4000 }
    );
  });

  it("on failed axios request to start a new chat, the start chat button becomes re-enabled if all inputs are still filled", async () => {
    vi.mock("axios", () => ({
      default: {
        post: vi.fn().mockRejectedValue(new Error("Connection Failed")),
      },
    }));

    await randomlyFillNewChatFormInputs(3);
    await userEvent.click(startChatButton);

    await waitFor(() => expect(startChatButton).toBeDisabled());
    await waitFor(() => expect(startChatButton).toBeEnabled(), {
      timeout: 4000,
    });
  });

  it("on failed axios request to start a new chat, the start chat button remains disabled if all inputs are not filled", async () => {
    vi.mock("axios", () => ({
      default: {
        post: vi.fn().mockRejectedValue(new Error("Connection Failed")),
      },
    }));

    await randomlyFillNewChatFormInputs(3);
    await userEvent.click(startChatButton);

    await userEvent.clear(groupChatNameInput);

    expect(startChatButton).toBeDisabled();
    await waitFor(() => expect(startChatButton).toBeDisabled(), {
      timeout: 4000,
    });
  });
});
