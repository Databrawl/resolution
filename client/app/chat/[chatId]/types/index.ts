import {UUID} from "crypto";

export type ChatQuestion = {
    chat_id: string;
    question: string;
};
export type ChatMessage = {
    chat_id: string;
    message_id: string;
    user_message: string;
    assistant: string;
    message_time: string;
};

type NotificationStatus = "Pending" | "Done";

export type Notification = {
    id: string;
    datetime: string;
    chat_id?: string | null;
    message?: string | null;
    action: string;
    status: NotificationStatus;
};

export type ChatMessageItem = {
    item_type: "MESSAGE";
    body: ChatMessage;
};

export type NotificationItem = {
    item_type: "NOTIFICATION";
    body: Notification;
};

export type ChatItem = ChatMessageItem | NotificationItem;

export type ChatEntity = {
    chat_id: UUID;
    user_id: string;
    creation_time: string;
    chat_name: string;
};
