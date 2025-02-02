import { ChatTitle } from "../../../components/ui/ChatTitle";

export default async function Chat({
  params,
}: {
  params: { chat_uuid: string };
}) {
  return (
    <div className={"pl-8 pt-8"}>
      <ChatTitle params={params} />
    </div>
  );
}
