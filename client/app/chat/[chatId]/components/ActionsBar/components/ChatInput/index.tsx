"use client";
import {useTranslation} from "react-i18next";

import Button from "@/lib/components/ui/Button";

import {OnboardingQuestions} from "./components";
import {ChatEditor} from "./components/ChatEditor/ChatEditor";
import {useChatInput} from "./hooks/useChatInput";

export const ChatInput = (): JSX.Element => {
    const {setMessage, submitQuestion, generatingAnswer, message} =
        useChatInput();

    const {t} = useTranslation(["chat"]);

    return (
        <>
            <OnboardingQuestions/>
            <div
                className="flex mt-1 flex-col w-full shadow-md dark:shadow-primary/25 hover:shadow-xl transition-shadow rounded-xl bg-input-back border border-black/10 dark:border-white/25 p-2">
                <form
                    data-testid="chat-input-form"
                    onSubmit={(e) => {
                        e.preventDefault();
                        submitQuestion();
                    }}
                    className="sticky bottom-0 w-full flex items-center gap-2 z-20 p-2"
                >
                    {/*Guardian: disable menu control button, as for now we don't have a menu*/}
                    {/*<MenuControlButton/>*/}

                    <div className="flex flex-1">
                        <ChatEditor
                            message={message}
                            setMessage={setMessage}
                            onSubmit={submitQuestion}
                        />
                    </div>

                    <div className="flex flex-row items-center gap-4">
                        <Button
                            className="px-3 py-2 sm:px-4 sm:py-2 bg-primary border-0 hover:bg-primary-hover"
                            type="submit"
                            isLoading={generatingAnswer}
                            data-testid="submit-button"
                        >
                            {generatingAnswer
                                ? t("thinking", {ns: "chat"})
                                : t("chat", {ns: "chat"})}
                        </Button>
                        {/*Guardian: disable Actions "+" button, as for now we don't provide these*/}
                        {/*<ActionsModal/>*/}
                    </div>
                </form>
            </div>
        </>
    );
};
