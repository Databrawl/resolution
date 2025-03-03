import {ChatMessage} from "@/app/chat/[chatId]/types";
import {useAxios} from "@/lib/hooks";

import {addQuestionAndAnswer, QuestionAndAnwser,} from "./addQuestionAndAnswer";
import {
    ChatUpdatableProperties,
    createChat,
    deleteChat,
    getChatItems,
    getChats,
    postMessage,
    updateChat,
} from "./chat";

// TODO: split './chat.ts' into multiple files, per function for example
// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const useChatApi = () => {
    const {axiosInstance} = useAxios();

    return {
        createChat: async (chatName: string) => createChat(chatName, axiosInstance),
        getChats: async () => getChats(axiosInstance),
        deleteChat: async (chatId: string) => deleteChat(chatId, axiosInstance),
        postMessage: async (props: ChatMessage) => postMessage(props, axiosInstance),
        getChatItems: async (chatId: string) => getChatItems(chatId, axiosInstance),
        updateChat: async (chatId: string, props: ChatUpdatableProperties) =>
            updateChat(chatId, props, axiosInstance),
        addQuestionAndAnswer: async (
            chatId: string,
            questionAndAnswer: QuestionAndAnwser
        ) => addQuestionAndAnswer(chatId, questionAndAnswer, axiosInstance),
    };
};
