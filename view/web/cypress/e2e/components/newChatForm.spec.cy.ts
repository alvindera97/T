describe("New Chat Form", () => {
  it("should redirect to the correct chat page after submitting the form", () => {
    const chatUUID = crypto.randomUUID();

    cy.intercept("POST", "http://localhost:8000/set_up_chat", {
      statusCode: 302,
      headers: {
        Location: `http://localhost:3000/chat/${chatUUID}`,
      },
    }).as("postChat");

    cy.visit("http://localhost:3000");

    cy.get("#new-group-chat-name").type("Test Chat");
    cy.get("#new-group-chat-context").type("Chat context here");
    cy.get("#new-group-chat-number-of-users").type("5");

    cy.get("#start-group-chat-btn").click();

    // Wait for the intercepted POST request to complete
    cy.wait("@postChat");

    cy.url().should("eq", `http://localhost:3000/chat/${chatUUID}`);
  });
});
