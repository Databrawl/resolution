import {UUID} from "crypto";
import {useParams, useRouter} from "next/navigation";
import {useEffect, useState} from "react";
import {useTranslation} from "react-i18next";

import {ChatMessage} from "@/app/chat/[chatId]/types";
import {useChatApi} from "@/lib/api/chat/useChatApi";
import {getChatNameFromQuestion} from "@/lib/helpers/getChatNameFromQuestion";
import {useOnboardingTracker} from "@/lib/hooks/useOnboardingTracker";

import {QuestionId} from "../../../types";
import {questionIdToTradPath} from "../utils";
import {useChatContext} from "@/lib/context";

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const useOnboardingQuestion = (questionId: QuestionId) => {
    const params = useParams();
    const {postMessage} = useChatApi();
    const {t} = useTranslation("chat");
    const {createChat} = useChatApi();
    const {updateChatHistory} = useChatContext();
    const {trackOnboardingEvent} = useOnboardingTracker();
    const [isAnswerRequested, setIsAnswerRequested] = useState(false);

    const [chatId, setChatId] = useState(params?.chatId as UUID | undefined);
    const router = useRouter();

    const onboardingStep = questionIdToTradPath[questionId];
    const question = t(`onboarding.${onboardingStep}`, {});
    // const answer = t(`onboarding.answer.${onboardingStep}`);

    // const {addQuestionAndAnswer} = useChatApi();
    // const {lastStream, isDone} = useStreamText({
    //     text: answer,
    //     enabled: isAnswerRequested && chatId !== undefined,
    // });

    // const addQuestionAndAnswerToChat = async () => {
    //     if (chatId === undefined) {
    //         return;
    //     }
    //
    //     // await addQuestionAndAnswer(chatId, {
    //     //     question: question,
    //     //     answer: answer,
    //     // });
    //     const shouldUpdateUrl = chatId !== params?.chatId;
    //     if (shouldUpdateUrl) {
    //         router.replace(`/chat/${chatId}`);
    //     }
    // };
    //
    // void addQuestionAndAnswerToChat();


    // useEffect(() => {
    //     if (!isDone) {
    //         return;
    //     }
    //     void addQuestionAndAnswerToChat();
    // }, [isDone]);

    useEffect(() => {
        if (chatId === undefined) {
            return;
        }

        if (isAnswerRequested) {
            setIsAnswerRequested(false);

            const chatMessage: ChatMessage = {
                message_id: new Date().getTime().toString(),
                chat_id: chatId,
                // message_id: questionId,
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
                    // setIsAnswerRequested(false);
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

            // void router.push(`/chat/${newChat.chat_id}`);
            // console.log("chatId is now", chatId);
            // console.log("the chatId from newChat is ", newChat.chat_id);
        }
        trackOnboardingEvent(onboardingStep);
        setIsAnswerRequested(true);

        // TODO: this uses PUT /onboarding API, that we don't have. Instead, we update the chat
        //  history with onboarding messages
        // await updateOnboarding({[questionId]: false});
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
