import { test, expect, type Page } from "@playwright/test";
import { chatUUID } from "../utils/functions";

/**
 * Helper: Fills the new chat form and optionally submits it
 *
 * @param page Playwright Page object for test of interest
 * @param submitForm if set to true, form to create new chat is submitted [default false].
 */
async function fillAllInputsForStartChatForm({
  page,
  submitForm = false,
}: {
  page: Page;
  submitForm?: boolean;
}) {
  await page
    .getByRole("textbox", { name: "Group chat name" })
    .fill("Test Chat");
  await page
    .getByRole("textbox", { name: "Chat context — General topic" })
    .fill("Chat context here");
  await page.getByPlaceholder("Number of group chat users").fill("5");

  if (submitForm) {
    await page.getByRole("button", { name: "Start chat" }).click();
  }
}

/**
 * Helper: Sets up a route to simulate a successful submission (redirect)
 *
 * @param page Playwright Page object for test of interest
 * @param delayedResponseTime if supplied, delays the mocked response to the requuest.
 */
async function setupSuccessRoute(page: Page, delayedResponseTime?: number) {
  await page.route("http://localhost:8000/set_up_chat", async (route) => {
    // Simulate a delay in response
    delayedResponseTime &&
      (await new Promise((resolve) =>
        setTimeout(resolve, delayedResponseTime)
      ));
    await route.fulfill({
      status: 302,
      headers: {
        Location: `http://localhost:3000/chat/${chatUUID}`,
      },
    });
  });
}

/**
 * Helper: Sets up a route that aborts requests
 *
 * @param page Playwright Page object for test of interest
 * @param url url for request to be aborted.
 */
async function setupAbortRoute(page: Page, url: string) {
  await page.route(url, async (route) => await route.abort());
}

/**
 * Helper: Asserts that the button text matches one of the expected states using regex
 *
 * @param page Playwright Page object for test of interest
 * @param selector Element HTML Selector
 * @param states Expected states element
 */
async function expectButtonStateMatches(
  page: Page,
  selector: string,
  states: string[]
) {
  const startChatButton = page.locator(selector);
  const regex = new RegExp(
    `^(${states.map((s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})$`
  );
  await expect(startChatButton).toHaveText(regex);
}

test.describe("Form for creating new group chat", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000");
  });

  test.describe("during submission", () => {
    test.describe("on successful form submission", () => {
      test("the text on the submit button changes during progress", async ({
        page,
      }) => {
        await setupSuccessRoute(page, 3000);

        await fillAllInputsForStartChatForm({ page, submitForm: true });

        const buttonStates = [
          "Setting up chat ...",
          "Please wait ...",
          "Starting chat ...",
        ];

        await expectButtonStateMatches(
          page,
          "#start-group-chat-btn",
          buttonStates
        );
      });

      test("should redirect to the correct chat page after submitting the form", async ({
        page,
      }) => {
        await setupSuccessRoute(page);
        await fillAllInputsForStartChatForm({ page, submitForm: true });

        await expect
          .poll(() => page.url())
          .toEqual(`http://localhost:3000/chat/${chatUUID}`);
      });
    });

    test.describe("on failed form submission", () => {
      test("submit button text returns to its initial state after a failed request", async ({
        page,
      }) => {
        await setupAbortRoute(page, "http://localhost:8000/_set_up_chat");
        await fillAllInputsForStartChatForm({ page, submitForm: true });

        const startChatButton = page.locator("#start-group-chat-btn");
        await expect(startChatButton).toHaveText("Start chat");
      });
    });

    test("should make a POST request for form submission", async ({ page }) => {
      let postRequestMade = false;

      page.on("request", (request) => {
        let requestPostData;
        try {
          requestPostData = request.postDataJSON();
        } catch {
          requestPostData = null;
        }

        if (
          request.method() === "POST" &&
          request.url() === "http://localhost:8000/set_up_chat" &&
          requestPostData &&
          requestPostData["chat_title"] === "Test Chat" &&
          requestPostData["chat_context"] === "Chat context here" &&
          requestPostData["chat_number_of_users"] === 5
        ) {
          postRequestMade = true;
        }
      });

      await setupAbortRoute(page, "http://localhost:8000/_set_up_chat");
      await fillAllInputsForStartChatForm({ page, submitForm: true });

      expect(postRequestMade).toBeTruthy();
    });
  });
});
