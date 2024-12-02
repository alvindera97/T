function fillAllInputsForStartChatForm({
  requestInterceptName,
  submitForm = false,
}: {
  requestInterceptName?: string;
  submitForm: boolean;
}) {
  cy.get("#new-group-chat-name").type("Test Chat");
  cy.get("#new-group-chat-context").type("Chat context here");
  cy.get("#new-group-chat-number-of-users").type("5");

  if (submitForm) {
    cy.get("#start-group-chat-btn").click();

    if (requestInterceptName) {
      cy.wait(`@${requestInterceptName}`);
    }
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
    const chatUUID = crypto.randomUUID();

    cy.intercept("POST", "*/set_up_chat", {
      statusCode: 302,
      headers: {
        Location: `http://localhost:3000/chat/${chatUUID}`,
      },
    }).as("postChat");

    fillAllInputsForStartChatForm({
      requestInterceptName: "postChat",
      submitForm: true,
    });

    cy.url().should("eq", `http://localhost:3000/chat/${chatUUID}`);
  });

  it("Asserts that the text on the submit button changes during progress", () => {
    cy.intercept("POST", "*/set_up_chat", {
      statusCode: 302,
      headers: {
        Location: `http://localhost:3000/chat/${crypto.randomUUID()}`,
      },
    }).as("postChat");

    fillAllInputsForStartChatForm({
      requestInterceptName: "postChat",
      submitForm: true,
    });

    cy.get("#start-group-chat-btn").should("have.text", "Setting up chat ...");
    cy.get("#start-group-chat-btn").should("have.text", "Please wait ...");
    cy.get("#start-group-chat-btn").should("have.text", "Starting chat ...");
  });

  it("Asserts that the submit button text returns to its initial state after a failed request", () => {
    cy.intercept("POST", "*/set_up_chat", {
      statusCode: 400,
    }).as("postChat2");

    cy.get("#start-group-chat-btn")
      .invoke("text")
      .then((initialText) => {
        fillAllInputsForStartChatForm({
          submitForm: true,
          requestInterceptName: "postChat2",
        });

        // Assert that the button text returns to its initial state
        cy.get("#start-group-chat-btn").should("have.text", initialText);
      });
  });
});
