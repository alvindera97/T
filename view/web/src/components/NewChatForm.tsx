"use client";

import { Button, Textarea, TextInput } from "flowbite-react";
import { useRef, useState } from "react";
import axios from "axios";
import { toast, Toaster } from "react-hot-toast";

export default function NewChatForm() {
  const [allInputsAreFilled, setAllInputsAreFilled] = useState(false);

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
          onChange={() => {
            setAllInputsAreFilled(checkAllInputsAreFilled());
          }}
        />
        <Textarea
          ref={newGroupChatContextInputRef}
          onChange={() => {
            setAllInputsAreFilled(checkAllInputsAreFilled());
          }}
          id="new-group-chat-context"
          placeholder="Chat context — General topic, mood and sentiment of the group chat."
        />
        <TextInput
          ref={newGroupChatNumberOfUsersInputRef}
          type="number"
          min={1}
          step={1}
          onChange={() => {
            setAllInputsAreFilled(checkAllInputsAreFilled());
          }}
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
          id="start-group-chat-btn"
          disabled={!allInputsAreFilled}
          onClick={(e: { preventDefault: () => void }) => {
            e.preventDefault();
            if (allInputsAreFilled) {
              setAllInputsAreFilled(false);
              axios
                .post(`${process.env.NEXT_PUBLIC_T_BACKEND_URL}/set_up_chat`, {
                  chat_context: "group chat context",
                })
                .then()
                .catch(() => {
                  setTimeout(() => {
                    toast.error(
                      "An error occurred while setting up your chat",
                      {
                        duration: 4000,
                      }
                    );
                    setTimeout(
                      () => setAllInputsAreFilled(checkAllInputsAreFilled()),
                      2000
                    );
                  }, 1500);
                });
            }
          }}
          className={`all-inputs-are-filled-${allInputsAreFilled}`}
        >
          Start chat
        </Button>
      </form>
    </>
  );
}
