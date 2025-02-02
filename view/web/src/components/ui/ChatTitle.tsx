"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import Image from "next/image";
import loadingGif from "../../icons8-loading.gif";

export const ChatTitle = ({ params }: { params?: { chat_uuid: string } }) => {
  const [chatTitle, setChatTitle] = useState<JSX.Element>(
    params && params.chat_uuid ? (
      <Image
        id={"chat-title-loading-gif"}
        width={30}
        height={30}
        alt={"Loading..."}
        src={loadingGif}
      />
    ) : (
      <h1>Invalid Chat session</h1>
    )
  );

  useEffect(() => {
    if (params && params.chat_uuid) {
      const resolveChatTitle = async () => {
        setChatTitle(
          await axios
            .post(
              `${process.env.NEXT_PUBLIC_T_BACKEND_URL}` + "/get_chat_info/",
              {
                chat_uuid: params.chat_uuid,
              }
            )
            .then(function (res) {
              return (
                <h1 className={"text-2xl"} id={"chat-title"}>
                  {res.data.chat_title}
                </h1>
              );
            })
            .catch(() => (
              <p className={"italic text-red-600"}>
                Click to re-fetch chat title
              </p>
            ))
        );
      };
      resolveChatTitle();
    }
  }, []);

  return chatTitle;
};
