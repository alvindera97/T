"use client";

import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import Image from "next/image";
import loadingGif from "../../icons8-loading.gif";
import { fetchChatTitleAgain } from "../../utils";

const TTNRComponent = ({ nextRequestTime }: { nextRequestTime: Date }) => {
  const [ttnr, setTtnr] = useState(
    Number(
      ((nextRequestTime.getTime() - new Date().getTime()) / 1000).toFixed(0)
    )
  );

  useEffect(() => {
    const intervalId = setInterval(() => {
      setTtnr((previousTime) => {
        if (previousTime > 0) {
          return Number(
            ((nextRequestTime.getTime() - new Date().getTime()) / 1000).toFixed(
              0
            )
          );
        }
        clearInterval(intervalId);
        return 0;
      });

      return () => clearInterval(intervalId);
    }, 1000);
  }, [ttnr]);

  return (
    <p className={"text-2xl"} id={"chat-title"}>
      Please try again in: {ttnr}s
    </p>
  );
};

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

  const nonRateLimitedFailureComponent = (
    content: string = "Check that you have a stable internet connection and click to re-fetch chat title"
  ) =>
    params && params.chat_uuid ? (
      <p
        onClick={() => fetchChatTitleAgain(params.chat_uuid)}
        className={"italic text-red-600 cursor-pointer"}
      >
        {content}
      </p>
    ) : (
      <></>
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
              console.log("res.data", JSON.stringify(res.data));
              if (res.data[params.chat_uuid] !== undefined) {
                setTimeout(
                  () =>
                    setChatTitle(
                      nonRateLimitedFailureComponent(
                        "Click to re-fetch chat title"
                      )
                    ),
                  new Date(res.data[params.chat_uuid]).getTime() -
                    new Date().getTime()
                );

                return (
                  <TTNRComponent
                    nextRequestTime={new Date(res.data[params.chat_uuid])}
                  />
                );
              }
              return (
                <h1 className={"text-2xl"} id={"chat-title"}>
                  {res.data.chat_title}
                </h1>
              );
            })
            .catch((error) => {
              if (error.data === null || error.data === undefined) {
                return nonRateLimitedFailureComponent();
              }
              if (Object.keys(error.data).length === 0) {
                return (
                  <p className={"text-2xl text-red-600"} id={"chat-title"}>
                    There is no such active chat: {params.chat_uuid}
                  </p>
                );
              }
              return nonRateLimitedFailureComponent();
            })
        );
      };
      resolveChatTitle();
    }
  }, []);

  return chatTitle;
};
