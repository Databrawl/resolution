import {useChatApi} from "@/lib/api/chat/useChatApi";
import {useChatContext} from "@/lib/context";
import {useToast} from "@/lib/hooks";

import type {ChatMessage, ChatQuestion} from "../types";
import {generatePlaceHolderMessage} from "../utils/generatePlaceHolderMessage";

interface UseChatService {
    addQuestion: (
        chatId: string,
        chatQuestion: ChatQuestion
    ) => Promise<void>;
}

export const useQuestion = (): UseChatService => {
    const {publish} = useToast();
    const {updateChatHistory} = useChatContext();
    const {postMessage} = useChatApi();

    const addQuestion = async (
        chatId: string,
        chatQuestion: ChatQuestion
    ): Promise<void> => {
        const userMessage = generatePlaceHolderMessage({
            user_message: chatQuestion.question,
            chat_id: chatId,
        });
        updateChatHistory(userMessage);

        try {
            const responseMessage: ChatMessage = await postMessage(userMessage);
            updateChatHistory(responseMessage);
        } catch (error) {
            // TODO: Move error handling to error.tsx
            publish({
                variant: "danger",
                text: String(error),
            });
        }
    };

    return {
        addQuestion
    };
};
