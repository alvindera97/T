import { chatUUID } from "../../support/e2e";

function fillAllInputsForStartChatForm({
  submitForm = false,
}: {
  submitForm: boolean;
}) {
  cy.get("#new-group-chat-name").type("Test Chat");
  cy.get("#new-group-chat-context").type("Chat context here");
  cy.get("#new-group-chat-number-of-users").type("5");

  if (submitForm) {
    cy.get("#start-group-chat-btn").click();
  }
}

describe("New Chat Form", () => {
  beforeEach(() => {
    cy.visit("http://localhost:3000");
  });

  afterEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
    cy.window().then((win) => {
      win.sessionStorage.clear();
    });
  });

  it("should redirect to the correct chat page after submitting the form", () => {
    fillAllInputsForStartChatForm({
      submitForm: true,
    });

    cy.url().should("eq", `http://localhost:3000/chat/${chatUUID}`);
  });

  it("Asserts that the text on the submit button changes during progress", () => {
    fillAllInputsForStartChatForm({
      submitForm: true,
    });

    cy.get("#start-group-chat-btn").should("have.text", "Setting up chat ...");
    cy.get("#start-group-chat-btn").should("have.text", "Please wait ...");
    cy.get("#start-group-chat-btn").should("have.text", "Starting chat ...");
  });

  it("Asserts that the submit button text returns to its initial state after a failed request", () => {
    cy.get("#start-group-chat-btn")
      .invoke("text")
      .then((initialText) => {
        fillAllInputsForStartChatForm({
          submitForm: true,
        });

        // Assert that the button text returns to its initial state
        cy.get("#start-group-chat-btn").should("have.text", initialText);
      });
  });
});
