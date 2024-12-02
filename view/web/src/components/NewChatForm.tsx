"use client";

import { Button, Textarea, TextInput } from "flowbite-react";
import { useRef, useState } from "react";
import axios from "axios";
import { toast, Toaster } from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function NewChatForm() {
  type StartNewChatSubmitButtonText =
    | "Start chat"
    | "Setting up chat ..."
    | "Please wait ..."
    | "Starting chat ...";
  const router = useRouter();
  const [requestInProgress, setRequestInProgress] = useState(false);
  const [allInputsAreFilled, setAllInputsAreFilled] = useState(false);
  const [submitButtonTextContent, setSubmitButtonTextContent] =
    useState<StartNewChatSubmitButtonText>("Start chat");
  const [submitButtonTextOpacity, setSubmitButtonTextOpacity] = useState(100);

  const formRef = useRef<HTMLFormElement>(null);
  const newGroupChatNameInputRef = useRef<HTMLInputElement>(null);
  const newGroupChatContextInputRef = useRef<HTMLTextAreaElement>(null);
  const newGroupChatNumberOfUsersInputRef = useRef<HTMLInputElement>(null);

  function checkAllInputsAreFilled() {
    return (
      newGroupChatNameInputRef!.current!.value.length *
        newGroupChatContextInputRef!.current!.value.length *
        newGroupChatNumberOfUsersInputRef!.current!.value.length >
      0
    );
  }

  function handleFormInputEvent() {
    if (!requestInProgress) setAllInputsAreFilled(checkAllInputsAreFilled);
  }

  async function updateSubmitButtonText(newText: StartNewChatSubmitButtonText) {
    if (newText !== "Setting up chat ...") setSubmitButtonTextOpacity(0);
    setSubmitButtonTextContent(newText);
    setTimeout(() => {
      setSubmitButtonTextOpacity(100);
    }, 200);
  }

  return (
    <>
      <Toaster position={"top-right"} reverseOrder={false} />
      <form
        ref={formRef}
        className="flex flex-col gap-y-2"
        id="new-chat-form"
        role="start-new-chat-form"
      >
        <TextInput
          ref={newGroupChatNameInputRef}
          placeholder="Group chat name"
          type="text"
          id="new-group-chat-name"
          onChange={handleFormInputEvent}
        />
        <Textarea
          ref={newGroupChatContextInputRef}
          onChange={handleFormInputEvent}
          id="new-group-chat-context"
          placeholder="Chat context — General topic, mood and sentiment of the group chat."
        />
        <TextInput
          ref={newGroupChatNumberOfUsersInputRef}
          type="number"
          min={1}
          step={1}
          onChange={handleFormInputEvent}
          onKeyDown={(e) => {
            if (
              !(
                (e.key >= "0" && e.key <= "9") ||
                e.key === "Backspace" ||
                e.key === "ArrowLeft" ||
                e.key === "ArrowRight" ||
                e.key === "Tab"
              ) ||
              (e.key >= "0" &&
                e.key <= "9" &&
                Number(e.currentTarget.value + e.key) < 1)
            ) {
              e.preventDefault();
            }
          }}
          id="new-group-chat-number-of-users"
          placeholder="Number of group chat users"
        />

        <Button
          type={"submit"}
          id="start-group-chat-btn"
          disabled={!allInputsAreFilled}
          onClick={async (e: { preventDefault: () => void }) => {
            setRequestInProgress(true);
            e.preventDefault();
            if (allInputsAreFilled) {
              setAllInputsAreFilled(false);
              await updateSubmitButtonText("Setting up chat ...");
              axios
                .post(`${process.env.NEXT_PUBLIC_T_BACKEND_URL}/set_up_chat`, {
                  chat_context: "group chat context",
                })
                .then((res) => {
                  setSubmitButtonTextContent("Please wait ...");
                  setTimeout(async () => {
                    await updateSubmitButtonText("Starting chat ...");
                    router.push(
                      res.request.responseURL.split("/").splice(-2).join("/")
                    );
                  }, 2000);
                })
                .catch(async () => {
                  setTimeout(() => {
                    toast.error(
                      <p>
                        {process.env
                          .NEXT_PUBLIC_CHAT_CREATION_FAILURE_MESSAGE !==
                        undefined
                          ? process.env
                              .NEXT_PUBLIC_CHAT_CREATION_FAILURE_MESSAGE
                          : "An error occurred while setting up your chat"}
                      </p>,
                      {
                        duration: 7000,
                      }
                    );
                    setTimeout(
                      () => setAllInputsAreFilled(checkAllInputsAreFilled()),
                      2000
                    );
                  }, 1500);
                  setRequestInProgress(false);
                  await updateSubmitButtonText("Start chat");
                });
            }
          }}
          className={`all-inputs-are-filled-${allInputsAreFilled}`}
        >
          <span
            style={{
              opacity: `${submitButtonTextOpacity}%`,
              transition: "opacity 1s ease",
            }}
          >
            {submitButtonTextContent}
          </span>
        </Button>
      </form>
    </>
  );
}
