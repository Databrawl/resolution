import {ChatMessage} from "@/app/chat/[chatId]/types";

import {MessageRow} from "./components";

type QADisplayProps = {
    content: ChatMessage;
};
export const QADisplay = ({content}: QADisplayProps): JSX.Element => {
    const {assistant, message_id, user_message} =
        content;

    return (
        <>
            <MessageRow
                key={`user-${message_id}`}
                speaker={"user"}
                text={user_message}
            />
            <MessageRow
                key={`assistant-${message_id}`}
                speaker={"assistant"}
                text={assistant}
            />
        </>
    );
};
