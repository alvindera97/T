import { describe, it, expect, vi, afterEach } from "vitest";
import { executeRandomCallable, fetchChatTitleAgain } from "../src/utils";
import { randomUUID } from "node:crypto";
import axios from "axios";

describe("executeRandomCallable() function", () => {
  const add = (a: number, b: number) => a + b;
  const multiply = (a: number, b: number) => a * b;

  it("specified number of random callables is executed", async () => {
    const callableList: CallableWithArgs[] = [
      [add, [2, 3]],
      [multiply, [4, 5]],
    ];

    vi.spyOn(Math, "random").mockReturnValueOnce(0.0).mockReturnValueOnce(0.5);

    const results = await executeRandomCallable(callableList, 2);

    expect(results).toEqual([5, 20]);
    expect(callableList.length).toBe(2);
  });

  it("throws error when n exceeds the length of the list", async () => {
    const callableList: CallableWithArgs[] = [[() => 1, []]];
    await expect(executeRandomCallable(callableList, 2)).rejects.toThrowError(
      "Cannot make more choices than the length of the list"
    );
  });

  it("returns an empty array for an empty input", async () => {
    const results = await executeRandomCallable([], 0);
    expect(results).toEqual([]);
  });

  it("handles functions with no arguments", async () => {
    const sayHello = () => "Hello!";
    const callableList: CallableWithArgs[] = [[sayHello, []]];
    const results = await executeRandomCallable(callableList, 1);
    expect(results).toEqual(["Hello!"]);
  });

  it("handles a mix of synchronous and asynchronous functions", async () => {
    const syncFn = (a: number) => a * 2;
    const asyncFn = async (name: string) => `Hello, ${name}!`;

    const callableList: CallableWithArgs[] = [
      [syncFn, [5]],
      [asyncFn, ["Alice"]],
    ];

    vi.spyOn(Math, "random").mockReturnValueOnce(0.0).mockReturnValueOnce(0.5);

    const results = await executeRandomCallable(callableList, 2);

    expect(results).toEqual([10, "Hello, Alice!"]);
  });

  it("does not modify the original input", async () => {
    const add = (a: number, b: number) => a + b;

    const callableList: CallableWithArgs[] = [
      [add, [1, 2]],
      [add, [3, 4]],
    ];

    const originalList = [...callableList];

    await executeRandomCallable(callableList, 1);

    expect(callableList).toEqual(originalList);
  });

  it("produces different results over multiple executions", async () => {
    const add = (a: number, b: number) => a + b;

    const callableList: CallableWithArgs[] = [
      [add, [1, 2]],
      [add, [3, 4]],
      [add, [5, 6]],
    ];

    const resultsSet = new Set();

    for (let i = 0; i < 10; i++) {
      const results = await executeRandomCallable(callableList, 2);
      resultsSet.add(JSON.stringify(results));
    }

    expect(resultsSet.size).toBeGreaterThan(1);
  });

  it("returns results in the order of execution", async () => {
    const callableList: CallableWithArgs[] = [
      [() => 1, []],
      [() => 2, []],
      [() => 3, []],
    ];

    vi.spyOn(Math, "random").mockReturnValueOnce(0.2).mockReturnValueOnce(0.0);

    const results = await executeRandomCallable(callableList, 2);

    expect(results).toEqual([1, 2]);
  });

  it("throws an error if n is less than 0", async () => {
    const callableList: CallableWithArgs[] = [
      [add, [1, 2]],
      [multiply, [3, 5]],
    ];

    vi.spyOn(Math, "random").mockReturnValueOnce(0.0).mockReturnValueOnce(0.5);

    expect(await executeRandomCallable(callableList, 0)).toEqual([]);

    await expect(executeRandomCallable(callableList, -1)).rejects.toThrowError(
      "Cannot make negative number of choices!"
    );
  });

  it("throws error if n is greater than number of callables", async () => {
    const callableList: CallableWithArgs[] = [
      [add, [10, 10]],
      [multiply, [33, 10]],
    ];

    vi.spyOn(Math, "random").mockReturnValueOnce(0.0).mockReturnValueOnce(0.5);
    await expect(
      executeRandomCallable(callableList, callableList.length + 1)
    ).rejects.toThrowError(
      "Cannot make more choices than the length of the list!"
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });
});

describe("fetchChatTitleAgain() function", () => {
  vi.mock("axios");
  describe("given the uuid of the chat", () => {
    const chatUUID = randomUUID();

    describe("regardless of the circumstances", () => {
      it("passes the given chatUUID in the request body", async () => {
        await fetchChatTitleAgain(chatUUID);
        expect(axios.post).toHaveBeenCalledWith(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/get_chat_info/`,
          { chat_uuid: chatUUID }
        );
      });
    });

    describe("if the user has been rate limited", () => {
      const earliestTimeForNextAllowedRequest = new Date(
        Date.now() + Number((Math.random() * 100).toFixed(0)) * 1000
      );
      it("returns message saying to try later in n seconds where n is a countdown of the time till the user can be allowed to make the request again", async () => {
        vi.mocked(axios.post).mockResolvedValue({
          data: {
            chatUUID: earliestTimeForNextAllowedRequest,
          },
        });
        expect(await fetchChatTitleAgain(chatUUID)).toEqual({
          chatUUID: earliestTimeForNextAllowedRequest,
        });
      });
    });

    describe("if the user has not been rate limited", () => {
      describe("if the chat exists", () => {
        it("returns an object with the correct title of the chat and a render color [for an existing chat this will be 'green']", async () => {
          vi.mocked(axios.post).mockResolvedValue({
            data: {
              chat_title: "hello world",
            },
          });
          expect(await fetchChatTitleAgain(chatUUID)).toEqual({
            chat_title: "hello world",
          });
        });
      });

      describe("if the chat doesn't exist", () => {
        it("returns an object with a string saying that the chat doesn't exist and a render color [for a non existing chat this will be 'red']", async () => {
          vi.mocked(axios.post).mockRejectedValue({});
          expect(await fetchChatTitleAgain(chatUUID)).toEqual({
            error: `There is no currently ongoing chat with the ID: ${chatUUID}`,
          });
        });
      });
    });
  });
});
