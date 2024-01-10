import {useTranslation} from "react-i18next";

import {useChatContext} from "@/lib/context";
import {useFetch, useToast} from "@/lib/hooks";
import {ChatQuestion} from "../types";
import {generatePlaceHolderMessage} from "../utils/generatePlaceHolderMessage";

interface UseChatService {
    send: (
        chatId: string,
        chatQuestion: ChatQuestion
    ) => Promise<void>;
}

export const useQuestion = (): UseChatService => {
    const {fetchInstance} = useFetch();

    const {t} = useTranslation(["chat"]);
    const {publish} = useToast();
    const {updateStreamingHistory} = useChatContext();

    const handleFetchError = async (response: Response) => {
        if (response.status === 429) {
            publish({
                variant: "danger",
                text: t("tooManyRequests", {ns: "chat"}),
            });

            return;
        }

        const errorMessage = (await response.json()) as { detail: string };
        publish({
            variant: "danger",
            text: errorMessage.detail,
        });
    };

    const send = async (
        chatId: string,
        chatQuestion: ChatQuestion
    ): Promise<void> => {
        const headers = {
            "Content-Type": "application/json",
            // Accept: "text/event-stream",
        };

        const placeHolderMessage = generatePlaceHolderMessage({
            user_message: chatQuestion.message ?? "",
            chat_id: chatId,
        });
        updateStreamingHistory(placeHolderMessage);

        const body = JSON.stringify(chatQuestion);

        try {
            const response = await fetchInstance.post(
                `/send`,
                body,
                headers
            );
            if (!response.ok) {
                void handleFetchError(response);

                return;
            }

            if (response.body === null) {
                throw new Error(t("resposeBodyNull", {ns: "chat"}));
            }

            //TODO: fix ChatMessage and enable this
            // const responseBody: never = await response.json();
            // const message = ChatMessage.fromJSON(responseBody);
            //
            // updateStreamingHistory(message);
        } catch (error) {
            publish({
                variant: "danger",
                text: String(error),
            });
        }
    };

    return {
        send,
    };
};
