"use client";

import React, { useEffect, useState } from "react";

export default function Chat({ params }: { params: { chat_uuid: string } }) {
  const [chatUuid, setChatUuid] = useState<string | null>(null);

  useEffect(() => {
    if (params.chat_uuid) {
      setChatUuid(params.chat_uuid); // Directly access the chat_uuid
    }
  }, [params]);

  if (!chatUuid) {
    return <div>Loading...</div>;
  }

  return (
    <div className={"pl-8 pt-8"}>
      <h1 className={"text-7xl"}>Hello world</h1>
      <p>
        Chat UUID: <span className={"text-semibold text-3xl"}>{chatUuid}</span>
      </p>
    </div>
  );
}
