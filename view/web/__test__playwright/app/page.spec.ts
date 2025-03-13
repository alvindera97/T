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
      let allowed_post_time = new Date(
        new Date().getTime() + Number((Math.random() * 30000).toFixed(0))
      );
      test.describe("if rate limited", () => {
        test("render countdown to next request time after which component changes to non-rate-limited failure state.", async ({
          page,
        }) => {
          await page.route(
            "http://localhost:8000/get_chat_info/",
            async (route) =>
              route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify({
                  [chatUUID]: allowed_post_time,
                }),
              })
          );

          await page.goto(`http://localhost:3000/chat/${chatUUID}`);
          for (
            var time = Number(
              (
                (allowed_post_time.getTime() - new Date().getTime()) /
                1000
              ).toFixed(0)
            );
            time > 0;
            time--
          ) {
            await expect(
              page.getByText(`Please try again in: ${time}s`)
            ).toBeVisible();
            await expect
              .poll(async () => {
                const text = await page
                  .getByText(`Please try again in: ${time}s`)
                  .isVisible();
                return text;
              })
              .toBe(true);
            await page.waitForTimeout(800);
          }
        });
      });
    });
  });
});
