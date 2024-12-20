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

function interceptSuccessfulRequestToCreateNewGroupChat() {
  cy.intercept(
    {
      method: "POST",
      url: `${Cypress.env("T_BACKEND_URL")}/set_up_chat`,
      // url: `**`,
    },
    (req) => {
      req.on("response", (res) => {
        res.setDelay(100);
      });
      req.reply({
        statusCode: 302,
        headers: {
          Location: `http://localhost:3000/chat/${chatUUID}`,
        },
      });
    }
  ).as("successfulNewChatCreationRequest");
}

function interceptFailedRequestToCreateNewGroupChat() {
  cy.intercept(
    {
      method: "POST",
      url: `${Cypress.env("T_BACKEND_URL")}/set_up_chat`,
    },
    (req) => {
      req.on("response", (res) => {
        res.setDelay(1000);
      });
      req.reply({ statusCode: 400 });
    }
  ).as("failedNewChatCreationRequest");
}

describe("Form for creating new group chat", () => {
  beforeEach(() => {
    interceptSuccessfulRequestToCreateNewGroupChat();
    cy.visit("http://localhost:3000");
  });

  afterEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
    cy.window().then((win) => {
      win.sessionStorage.clear();
    });
  });

  describe("during submission", () => {
    describe("on successful form submission", () => {
      beforeEach(() => {
        interceptSuccessfulRequestToCreateNewGroupChat();
        cy.visit("http://localhost:3000");
      });

      it("the text on the submit button changes during progress", () => {
        interceptSuccessfulRequestToCreateNewGroupChat();
        fillAllInputsForStartChatForm({
          submitForm: true,
        });

        cy.get("#start-group-chat-btn").should(
          "have.text",
          "Setting up chat ..."
        );
        cy.get("#start-group-chat-btn").should("have.text", "Please wait ...");
        cy.get("#start-group-chat-btn").should(
          "have.text",
          "Starting chat ..."
        );
      });

      it("should redirect to the correct chat page after submitting the form", () => {
        interceptSuccessfulRequestToCreateNewGroupChat();
        fillAllInputsForStartChatForm({
          submitForm: true,
        });

        cy.url().should("eq", `http://localhost:3000/chat/${chatUUID}`);
      });
    });

    describe("on failed form submission", () => {
      beforeEach(() => {
        interceptFailedRequestToCreateNewGroupChat();
        cy.visit("http://localhost:3000");
      });

      it("submit button text returns to its initial state after a failed request", () => {
        interceptFailedRequestToCreateNewGroupChat();
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

    it("should make a POST request for form submission", () => {
      fillAllInputsForStartChatForm({
        submitForm: true,
      });

      cy.wait("@successfulNewChatCreationRequest", { timeout: 10000 })
        .its("request.body")
        .then((body) => {
          expect(body.chat_context).to.equal("Chat context here");
          expect(body.chat_title).to.equal("Test Chat");
          expect(body.chat_number_of_users).to.equal(5);
        });
    });
  });
});
