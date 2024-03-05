import {UUID} from "crypto";
import {useParams, useRouter} from "next/navigation";
import {useEffect, useState} from "react";

import {ChatMessage} from "@/app/chat/[chatId]/types";
import {useChatApi} from "@/lib/api/chat/useChatApi";
import {useOnboardingApi} from "@/lib/api/onboarding/useOnboardingApi";
import {useChatContext} from "@/lib/context";
import {getChatNameFromQuestion} from "@/lib/helpers/getChatNameFromQuestion";

import {QuestionId} from "../../../types";


// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const useOnboardingQuestion = (questionId: QuestionId) => {
    const params = useParams();
    const {postMessage} = useChatApi();
    const {getOnboardingData} = useOnboardingApi();

    const {createChat} = useChatApi();
    const {updateChatHistory} = useChatContext();
    const [isAnswerRequested, setIsAnswerRequested] = useState(false);
    const [question, setQuestion] = useState<string>('');

    const [chatId, setChatId] = useState(params?.chatId as UUID | undefined);
    const router = useRouter();

    useEffect(() => {
        getOnboardingData().then(data => {
            setQuestion(data[questionId]);
        }).catch((error) => {
            // Handle any errors that occur during postMessage or updateChatHistory
            console.error("Error retrieving Onboarding data:", error);
        });
    }, [getOnboardingData, questionId]);

    useEffect(() => {
        if (chatId === undefined) {
            return;
        }

        if (isAnswerRequested) {
            setIsAnswerRequested(false);

            const chatMessage: ChatMessage = {
                message_id: new Date().getTime().toString(),
                chat_id: chatId,
                assistant: "",
                user_message: question,
                message_time: Date.now().toLocaleString(),
            };
            void updateChatHistory(chatMessage);

            postMessage(chatMessage)
                .then((responseMessage) => {
                    // this should be the same as chatMessage
                    if (responseMessage.assistant === undefined) {
                        console.log("response message is undefined! Something is wrong!");
                    }
                    void updateChatHistory(responseMessage);
                })
                .catch((error) => {
                    // Handle any errors that occur during postMessage or updateChatHistory
                    console.error("Error updating chat history:", error);
                });
        }
    }, [isAnswerRequested, question, questionId, postMessage]);

    const handleSuggestionClick = async () => {
        if (chatId === undefined) {
            const newChat = await createChat(getChatNameFromQuestion(question));
            setChatId(newChat.chat_id);
        }
        setIsAnswerRequested(true);
    };

    useEffect(() => {
        console.log(chatId); // This will log the updated state after it changes
        const shouldUpdateUrl = chatId !== params?.chatId;
        if (shouldUpdateUrl) {
            router.replace(`/chat/${chatId}`);
        }
    }, [chatId, params?.chatId, router]); // This effect runs every time chatId changes

    return {
        handleSuggestionClick,
        question,
    };
};
