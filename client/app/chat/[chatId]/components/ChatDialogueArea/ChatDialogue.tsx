import {useChatContext} from "@/lib/context";

import {ChatDialogue} from "./components/ChatDialogue";
import {
    getMergedChatMessagesWithDoneStatusNotificationsReduced
} from "./utils/getMergedChatMessagesWithDoneStatusNotificationsReduced";

export const ChatDialogueArea = (): JSX.Element => {
    const {messages, notifications} = useChatContext();

    const chatItems = getMergedChatMessagesWithDoneStatusNotificationsReduced(
        messages,
        notifications
    );
    // Guardian: This logic displays a chat dialogue area if there are messages in the chat, otherwise it displays
    // shortcuts. Shortcuts is basically a couple of text pieces: command button icon on top, and some shortcut examples
    // in the middle of the screen. It's all rendered on the base canvas, so the style is nicely preserved.

    // import {useOnboarding} from "@/lib/hooks/useOnboarding";
    // import {ShortCuts} from "./components/ShortCuts";
    // const {isOnboarding} = useOnboarding();

    // const shouldDisplayShortcuts = chatItems.length === 0 && !isOnboarding;
    //
    // if (!shouldDisplayShortcuts) {
    //     return <ChatDialogue chatItems={chatItems}/>;
    // }
    //
    // return <ShortCuts/>;

    return <ChatDialogue chatItems={chatItems}/>;

};
