/* eslint-disable max-lines */
import {renderHook} from "@testing-library/react";
import {afterEach, describe, expect, it, vi} from "vitest";

import {ChatMessage} from "@/app/chat/[chatId]/types";

import {useChatApi} from "../useChatApi";

const axiosPostMock = vi.fn(() => ({}));
const axiosGetMock = vi.fn(() => ({}));
const axiosPutMock = vi.fn(() => ({}));
const axiosDeleteMock = vi.fn(() => ({}));

vi.mock("@/lib/hooks", () => ({
    useAxios: () => ({
        axiosInstance: {
            post: axiosPostMock,
            get: axiosGetMock,
            put: axiosPutMock,
            delete: axiosDeleteMock,
        },
    }),
}));

describe("useChatApi", () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it("should call createChat with the correct parameters", async () => {
        const chatName = "Test Chat";
        axiosPostMock.mockReturnValue({data: {}});
        const {
            result: {
                current: {createChat},
            },
        } = renderHook(() => useChatApi());
        await createChat(chatName);

        expect(axiosPostMock).toHaveBeenCalledTimes(1);
        expect(axiosPostMock).toHaveBeenCalledWith("/chats", {
            name: chatName,
        });
    });

    it("should call getChats with the correct parameters", async () => {
        axiosGetMock.mockReturnValue({data: {}});
        const {
            result: {
                current: {getChats},
            },
        } = renderHook(() => useChatApi());

        await getChats();

        expect(axiosGetMock).toHaveBeenCalledTimes(1);
        expect(axiosGetMock).toHaveBeenCalledWith("/chats");
    });

    it("should call deleteChat with the correct parameters", async () => {
        const chatId = "test-chat-id";
        axiosDeleteMock.mockReturnValue({});
        const {
            result: {
                current: {deleteChat},
            },
        } = renderHook(() => useChatApi());

        await deleteChat(chatId);

        expect(axiosDeleteMock).toHaveBeenCalledTimes(1);
        expect(axiosDeleteMock).toHaveBeenCalledWith(`/chats/${chatId}`);
    });

    it("should call addQuestion with the correct parameters", async () => {
        const chatMessage: ChatMessage = {
            chat_id: "test-chat-id",
            message_id: "test-message-id",
            user_message: "Hello, how are you?",
            assistant: "",
            message_time: "2021-01-01T00:00:00.000Z",
        };

        const {
            result: {
                current: {postMessage},
            },
        } = renderHook(() => useChatApi());

        await postMessage(chatMessage);

        expect(axiosPostMock).toHaveBeenCalledTimes(1);
        expect(axiosPostMock).toHaveBeenCalledWith(
            `/messages`,
            chatMessage
        );
    });

    it("should call getHistory with the correct parameters", async () => {
        const chatId = "test-chat-id";
        axiosGetMock.mockReturnValue({data: {}});
        const {
            result: {
                current: {getChatItems: getHistory},
            },
        } = renderHook(() => useChatApi());

        await getHistory(chatId);

        expect(axiosGetMock).toHaveBeenCalledTimes(1);
        expect(axiosGetMock).toHaveBeenCalledWith(`/chats/${chatId}/history`);
    });

    it("should call updateChat with the correct parameters", async () => {
        const chatId = "test-chat-id";
        const chatName = "test-chat-name";
        axiosPutMock.mockReturnValue({data: {}});
        const {
            result: {
                current: {updateChat},
            },
        } = renderHook(() => useChatApi());

        await updateChat(chatId, {chat_name: chatName});

        expect(axiosPutMock).toHaveBeenCalledTimes(1);
        expect(axiosPutMock).toHaveBeenCalledWith(`/chats/${chatId}/metadata`, {
            chat_name: chatName,
        });
    });

    it("should call addQuestionAndAnswer with the correct parameters", async () => {
        const chatId = "test-chat-id";
        const question = "test-question";
        const answer = "test-answer";
        axiosPostMock.mockReturnValue({data: {}});
        const {
            result: {
                current: {addQuestionAndAnswer},
            },
        } = renderHook(() => useChatApi());

        await addQuestionAndAnswer(chatId, {question, answer});

        expect(axiosPostMock).toHaveBeenCalledTimes(1);
        expect(axiosPostMock).toHaveBeenCalledWith(
            `/chats/${chatId}/question/answer`,
            {question, answer}
        );
    });
});
