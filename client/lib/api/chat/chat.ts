import {AxiosInstance} from "axios";

import {ChatEntity, ChatItem, ChatMessage} from "@/app/chat/[chatId]/types";

export const createChat = async (
    name: string,
    axiosInstance: AxiosInstance
): Promise<ChatEntity> => {
    const response = await axiosInstance.post<ChatEntity>("/chats", {name});

    return response.data;
};

export const getChats = async (
    axiosInstance: AxiosInstance
): Promise<ChatEntity[]> => {
    const response = await axiosInstance.get<{
        chats: ChatEntity[];
    }>(`/chats`);

    return response.data.chats;
};

export const deleteChat = async (
    chatId: string,
    axiosInstance: AxiosInstance
): Promise<void> => {
    await axiosInstance.delete(`/chats/${chatId}`);
};

export const postMessage = async (
    chatMessage: ChatMessage,
    axiosInstance: AxiosInstance
): Promise<ChatMessage> => {
    const response = await axiosInstance.post<ChatMessage>(
        `/messages`,
        chatMessage
    );

    return response.data;
};

export const getChatItems = async (
    chatId: string,
    axiosInstance: AxiosInstance
): Promise<ChatItem[]> =>
    (await axiosInstance.get<ChatItem[]>(`/chats/${chatId}/history`)).data;

export type ChatUpdatableProperties = {
    chat_name?: string;
};
export const updateChat = async (
    chatId: string,
    chat: ChatUpdatableProperties,
    axiosInstance: AxiosInstance
): Promise<ChatEntity> => {
    return (await axiosInstance.put<ChatEntity>(`/chats/${chatId}/metadata`, chat))
        .data;
};
