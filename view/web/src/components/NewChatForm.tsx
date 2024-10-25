import { Button } from "flowbite-react";
export default function NewChatForm() {
  return (
    <form
      className="flex flex-col gap-y-2"
      action={"POST"}
      id="new-chat-form"
      role="start-new-chat-form"
    >
      <input
        placeholder="Group chat name"
        type="text"
        id="new-group-chat-name"
      />
      <textarea
        id="new-group-chat-context"
        placeholder="Chat context — General topic, mood and sentiment of the group chat."
      />
      <input
        type="number"
        min={1}
        step={1}
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

      <Button id="start-group-chat-btn" type="submit">
        Start chat
      </Button>
    </form>
  );
}
