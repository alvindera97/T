import { expect, test } from "@playwright/test";
import { faker } from "@faker-js/faker";

import { chatUUID } from "../utils/functions";

export const TEST_CHAT_TITLE = faker.lorem
  .sentence()
  .toString()
  .toLowerCase()
  .replace(/\b\w/g, (char) => char.toUpperCase());

test.describe("Chat interface", () => {
  test.describe("on load", () => {
    test.describe("on successful chat detail fetch", () => {
      test("should render chat title", async ({ page }) => {
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
            request.url() === "http://localhost:8000/get_chat_info/" &&
            requestPostData &&
            requestPostData["chat_uuid"] === chatUUID
          ) {
            postRequestMade = true;
          }
        });

        await page.route(
          "http://localhost:8000/get_chat_info/",
          async (route) => {
            await new Promise((resolve) => setTimeout(resolve, 100));
            await route.fulfill({
              status: 200,
              json: { chat_title: TEST_CHAT_TITLE },
            });
          }
        );
        await page.goto(`http://localhost:3000/chat/${chatUUID}`);
        await expect.poll(() => postRequestMade).toBeTruthy();
        await expect(page.locator("#chat-title")).toHaveText(TEST_CHAT_TITLE);
      });
    });

    test.describe("on failed chat detail fetch", () => {
      test("should render text showing asking user to click to reload the page title", async ({
        page,
      }) => {
        await page.route(
          "http://localhost:8000/get_chat_info/",
          async (route) => route.abort()
        );
        await page.goto(`http://localhost:3000/chat/${chatUUID}`);
        await expect(
          page.getByText("Click to re-fetch chat title")
        ).toBeVisible();
      });
    });
  });
});
