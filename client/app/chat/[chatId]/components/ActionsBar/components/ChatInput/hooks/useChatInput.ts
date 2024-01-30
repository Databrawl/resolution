import {useCallback, useState} from "react";

import {useChat} from "@/app/chat/[chatId]/hooks/useChat";

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const useChatInput = () => {
    const [message, setMessage] = useState<string>("");
    const {addChatQuestion, generatingAnswer, chatId} = useChat();

    const submitQuestion = useCallback(() => {
        if (!generatingAnswer) {
            void addChatQuestion(message, () => setMessage(""));
        }
    }, [addChatQuestion, generatingAnswer, message]);

    return {
        message,
        setMessage,
        submitQuestion,
        generatingAnswer,
        chatId,
    };
};
