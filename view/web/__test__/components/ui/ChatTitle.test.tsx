import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ChatTitle } from "../../../src/components/ui/ChatTitle";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";

const chatUUID = "511d7db6-c4ac-45fc-9a68-22e97cf58e99";

describe("<ChatTitle /> component", async () => {
  const TEST_CHAT_TITLE = await vi.hoisted(async () => {
    const { faker } = await import("@faker-js/faker");
    return faker.lorem.word();
  });

  vi.mock("axios");

  afterEach(() => {
    vi.resetAllMocks();
    cleanup();
  });

  describe("on render with all necessary props", () => {
    it("should fetch chat details thus rendering the 'loading' state", () => {
      vi.mocked(axios.post).mockResolvedValue({
        data: { chat_title: TEST_CHAT_TITLE },
      });

      const { container } = render(
        <ChatTitle params={{ chat_uuid: chatUUID }} />
      );
      const chatTitleLoadingGif = container
        .querySelectorAll("img#chat-title-loading-gif")
        ?.item(0);
      expect(chatTitleLoadingGif as HTMLImageElement).toBeInTheDocument();
      expect(chatTitleLoadingGif.getAttribute("alt")).equal("Loading...");
    });

    describe("on chat details fetch", () => {
      describe("on successful details fetch", () => {
        it("should render correctly fetched data", async () => {
          vi.mocked(axios.post).mockResolvedValue({
            data: { chat_title: TEST_CHAT_TITLE },
          });

          render(<ChatTitle params={{ chat_uuid: chatUUID }} />);

          await waitFor(
            () => {
              expect(
                document.querySelector(
                  "h1.text-2xl#chat-title"
                ) as HTMLHeadingElement
              ).toBeInTheDocument();
              expect(
                document.querySelector("h1.text-2xl#chat-title")?.textContent
              ).toEqual(TEST_CHAT_TITLE);
            },
            { interval: 5000 }
          );
        });
      });

      describe("on failed details fetch", () => {
        describe("it should render a failure state", () => {
          it("after 5 seconds of not being able to resolve the application title if there is a server connection", async () => {
            vi.mocked(axios.post).mockRejectedValue({ data: {} });

            render(<ChatTitle params={{ chat_uuid: chatUUID }} />);
            await waitFor(
              () => {
                const titleNotFoundText = screen.getByText(
                  "Click to re-fetch chat title"
                );
                expect(titleNotFoundText).toBeInTheDocument();
              },
              { timeout: 5000 }
            );
          });

          it("immediately if there is a failure in connecting to the server", async () => {
            vi.mocked(axios.post).mockRejectedValue(
              new Error("Connection Failed")
            );

            render(<ChatTitle params={{ chat_uuid: chatUUID }} />);

            await waitFor(
              () => {
                const titleNotFoundText = screen.getByText(
                  "Click to re-fetch chat title"
                );
                expect(titleNotFoundText).toBeInTheDocument();
              },
              {
                timeout: 1000,
              }
            );
          });
        });
      });
    });
  });

  describe("on render with missing params.chat_uuid", () => {
    it("should show invalid session message", () => {
      render(<ChatTitle />);
      expect(screen.getByText("Invalid Chat session")).toBeInTheDocument();
    });

    it("should not make any api calls.", () => {
      render(<ChatTitle />);
      expect(axios.post).not.toHaveBeenCalledOnce();
    });
  });
});
