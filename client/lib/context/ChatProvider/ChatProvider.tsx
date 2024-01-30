"use client";

import {createContext, useState} from "react";

import {ChatMessage, Notification} from "@/app/chat/[chatId]/types";

import {ChatContextProps} from "./types";

export const ChatContext = createContext<ChatContextProps | undefined>(
    undefined
);

export const ChatProvider = ({
                                 children,
                             }: {
    children: JSX.Element | JSX.Element[];
}): JSX.Element => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const updateChatHistory = (message: ChatMessage): void => {
        setMessages((prevHistory: ChatMessage[]) => {
            return prevHistory.find(
                (item) => item.message_id === message.message_id
            )
                ? prevHistory.map((item: ChatMessage) =>
                    item.message_id === message.message_id
                        // if we find the original user message, we update the assistant response
                        ? {...item, assistant: message.assistant}
                        : item
                )
                : [...prevHistory, message];
        });
    };

    const removeMessage = (id: string): void => {
        setMessages((prevHistory: ChatMessage[]) =>
            prevHistory.filter((item) => item.message_id !== id)
        );
    };

    return (
        <ChatContext.Provider
            value={{
                messages,
                setMessages,
                updateChatHistory,
                removeMessage,
                notifications,
                setNotifications,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};
