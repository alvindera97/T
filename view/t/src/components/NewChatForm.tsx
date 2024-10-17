export default function NewChatForm() {
  return (
    <form action={"POST"} id="new-chat-form" role="start-new-chat-form">
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
        id="new-group-chat-number-of-users"
        placeholder="Number of group chat users"
      />
      <button id="start-group-chat-btn" type="submit">
        Start chat
      </button>
    </form>
  );
}
