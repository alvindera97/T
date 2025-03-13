import { afterEach, describe, expect, it, vi } from "vitest";
import { ChatTitle } from "../../../src/components/ui/ChatTitle";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import userEvent from "@testing-library/user-event";
import { fetchChatTitleAgain } from "../../../src/utils";

const chatUUID = "511d7db6-c4ac-45fc-9a68-22e97cf58e99";

describe("<ChatTitle /> component", async () => {
  const TEST_CHAT_TITLE = await vi.hoisted(async () => {
    const { faker } = await import("@faker-js/faker");
    return faker.lorem.word();
  });

  vi.mock("axios");
  vi.mock("../../../src/utils");

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
      afterEach(() => {
        vi.resetAllMocks();
        cleanup();
      });
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
        afterEach(() => {
          vi.resetAllMocks();
          cleanup();
        });
        describe("if not rate limited", () => {
          afterEach(() => {
            vi.resetAllMocks();
            cleanup();
          });
          describe("it should render a failure state", () => {
            it("if no such current chat exists", async () => {
              vi.mocked(axios.post).mockRejectedValue({
                status: 400,
                data: {},
              });

              render(<ChatTitle params={{ chat_uuid: chatUUID }} />);
              await waitFor(
                async () => {
                  const titleNotFoundText = screen.getByText(
                    `There is no such active chat: ${chatUUID}`
                  );
                  expect(titleNotFoundText).toBeInTheDocument();
                },
                { timeout: 5000 }
              );
            });

            it("which is clickable if there is a failure in connecting to the server", async () => {
              vi.mocked(axios.post).mockRejectedValue(
                new Error("Connection Failed")
              );

              render(<ChatTitle params={{ chat_uuid: chatUUID }} />);

              await waitFor(
                () => {
                  const titleNotFoundText = screen.getByText(
                    "Check that you have a stable internet connection and click to re-fetch chat title"
                  );
                  expect(titleNotFoundText).toBeInTheDocument();
                  expect(titleNotFoundText.onclick).not.toBeNull();
                  expect(
                    titleNotFoundText.classList.contains("cursor-pointer")
                  ).toBeTruthy();
                },
                {
                  timeout: 1000,
                }
              );
            });

            describe("which when clicked", () => {
              let allowed_post_time = new Date(
                new Date().getTime() +
                  Number((Math.random() * 50000).toFixed(0))
              );

              describe("if chat exists", () => {
                describe("if the server is able to be reached", () => {
                  describe("if rate limited", () => {
                    it("should render the rate limited state", async () => {
                      vi.mocked(axios.post).mockResolvedValue({
                        data: {
                          [chatUUID]: allowed_post_time,
                        },
                      });

                      const { container } = render(
                        <ChatTitle params={{ chat_uuid: chatUUID }} />
                      );

                      await expect
                        .poll(
                          () =>
                            container.querySelector("p.text-2xl#chat-title")
                              ?.textContent
                        )
                        .toContain("Please try again in: ");
                    });
                  });

                  describe("if not rate limited", () => {
                    it("should render the chat title :)", async () => {
                      vi.mocked(axios.post).mockResolvedValue({
                        data: { chat_title: TEST_CHAT_TITLE },
                      });

                      const { container } = render(
                        <ChatTitle params={{ chat_uuid: chatUUID }} />
                      );
                      await expect
                        .poll(
                          () =>
                            container.querySelector("h1.text-2xl#chat-title")
                              ?.textContent,
                          { timeout: 3000 }
                        )
                        .toEqual(TEST_CHAT_TITLE);
                    });
                  });
                });

                describe("if the server is unable to be reached", () => {
                  it(
                    "renders a failures state asking the user to check their internet connection or try again later",
                    async () => {
                      vi.mocked(axios.post).mockRejectedValue(
                        new Error("Connection failed")
                      );
                      const { container } = render(
                        <ChatTitle params={{ chat_uuid: chatUUID }} />
                      );
                      await expect
                        .poll(
                          () =>
                            container.querySelector(
                              "p.italic.text-red-600.cursor-pointer"
                            )!.textContent,
                          {
                            timeout:
                              allowed_post_time.getTime() -
                              new Date().getTime() +
                              2000,
                          }
                        )
                        .toEqual(
                          "Check that you have a stable internet connection and click to re-fetch chat title"
                        );
                    },
                    {
                      timeout:
                        allowed_post_time.getTime() -
                        new Date().getTime() +
                        2000,
                    }
                  );
                });
              });

              describe("if chat doesn't exist", () => {
                describe("if rate limited", () => {
                  it("should render the rate limited state", async () => {
                    vi.mocked(axios.post).mockResolvedValue({
                      data: {
                        [chatUUID]: allowed_post_time,
                      },
                    });

                    const { container } = render(
                      <ChatTitle params={{ chat_uuid: chatUUID }} />
                    );

                    await expect
                      .poll(
                        () =>
                          container.querySelector("p.text-2xl#chat-title")
                            ?.textContent,
                        { timeout: 3000 }
                      )
                      .toContain("Please try again in: ");
                  });
                });

                describe("if not rate limited", () => {
                  it("should render that the chat doesn't exist", async () => {
                    vi.mocked(axios.post).mockRejectedValue({ data: {} });
                    const { container } = render(
                      <ChatTitle params={{ chat_uuid: chatUUID }} />
                    );

                    await expect
                      .poll(
                        () =>
                          container.querySelector(
                            "p.text-2xl.text-red-600#chat-title"
                          )?.textContent
                      )
                      .toEqual(`There is no such active chat: ${chatUUID}`);
                  });
                });
              });
            });
          });
        });

        describe("if rate limited", () => {
          let allowed_post_time = new Date(
            new Date().getTime() + Number((Math.random() * 50000).toFixed(0))
          );

          it("renders rate limiting text with countdown to next allowed request time", async () => {
            vi.mocked(axios.post).mockResolvedValue({
              data: {
                [chatUUID]: allowed_post_time,
              },
            });

            const { container } = render(
              <ChatTitle params={{ chat_uuid: chatUUID }} />
            );

            expect(axios.post).toHaveBeenCalledWith(
              `${process.env.NEXT_PUBLIC_T_BACKEND_URL}/get_chat_info/`,
              { chat_uuid: chatUUID }
            );

            const maxCountdownTime_in_seconds =
              Number((new Date().getTime() / 1000).toFixed(0)) -
              Number((allowed_post_time.getTime() / 1000).toFixed(0));

            await expect
              .poll(
                () =>
                  container.querySelector("p.text-2xl#chat-title")?.textContent
              )
              .toContain("Please try again in: ");

            await expect
              .poll(() =>
                Number(
                  container
                    .querySelector("p.text-2xl#chat-title")!
                    .textContent!.split(" ")
                    .at(-1)!
                    .slice(0, -1)
                )
              )
              .toBeGreaterThan(0);

            expect.poll(
              () =>
                Number(
                  container
                    .querySelector("p.text-2xl#chat-title")!
                    .textContent!.split(" ")
                    .at(-1)!
                    .slice(0, -1)
                ) < maxCountdownTime_in_seconds
            );
          });

          it(
            "at the end of the countdown to next allowed request time, failure state reverts to the non-rate-limited-failure state [to allow the user to decide to reload the page or try getting the name of the chat again]",
            async () => {
              // test what happens after countdown is completed.
              vi.mocked(axios.post).mockResolvedValue({
                data: {
                  [chatUUID]: allowed_post_time,
                },
              });

              vi.mocked(fetchChatTitleAgain).mockResolvedValue({});

              const { container } = render(
                <ChatTitle params={{ chat_uuid: chatUUID }} />
              );

              await expect
                .poll(
                  () =>
                    container.querySelector("p.text-2xl#chat-title")
                      ?.textContent
                )
                .toContain("Please try again in: ");

              await expect
                .poll(
                  () =>
                    container.querySelector(
                      "p.italic.text-red-600.cursor-pointer"
                    )!.textContent,
                  {
                    timeout:
                      allowed_post_time.getTime() - new Date().getTime() + 2000,
                  }
                )
                .toEqual("Click to re-fetch chat title");

              await userEvent.click(
                container.querySelector(
                  "p.italic.text-red-600.cursor-pointer"
                ) as HTMLParagraphElement
              );
              expect(fetchChatTitleAgain).toHaveBeenCalledWith(chatUUID);
            },
            allowed_post_time.getTime() - new Date().getTime() + 2000
          );
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
