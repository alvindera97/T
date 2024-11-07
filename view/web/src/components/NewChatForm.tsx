"use client";

import { Button, Textarea, TextInput } from "flowbite-react";
import { useRef, useState } from "react";

export default function NewChatForm() {
  const [allInputsAreFilled, setAllInputsAreFilled] = useState(false);

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
    <form
      className="flex flex-col gap-y-2"
      action={"POST"}
      id="new-chat-form"
      role="start-new-chat-form"
    >
      <TextInput
        ref={newGroupChatNameInputRef}
        placeholder="Group chat name"
        type="text"
        id="new-group-chat-name"
        onChange={(e) => {
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
        onChange={(e) => {
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
        type="submit"
        id="start-group-chat-btn"
        disabled={!allInputsAreFilled}
        className={`all-inputs-are-filled-${allInputsAreFilled}`}
      >
        Start chat
      </Button>
    </form>
  );
}
