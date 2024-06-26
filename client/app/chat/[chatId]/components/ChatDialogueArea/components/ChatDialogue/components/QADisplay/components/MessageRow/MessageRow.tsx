import React from "react";
import {FaSpinner} from "react-icons/fa";

import {CopyButton} from "./components/CopyButton";
import {MessageContent} from "./components/MessageContent";
import {SourcesButton} from "./components/SourcesButton";
import {useMessageRow} from "./hooks/useMessageRow";


type MessageRowProps = {
    speaker: "user" | "assistant";
    text?: string;
    brainName?: string | null;
    promptName?: string | null;
    children?: React.ReactNode;
};

export const MessageRow = React.forwardRef(
    (
        {speaker, text, brainName}: MessageRowProps,
        ref: React.Ref<HTMLDivElement>
    ) => {
        const {
            containerClasses,
            containerWrapperClasses,
            handleCopy,
            isCopied,
            isUserSpeaker,
            markdownClasses,
        } = useMessageRow({
            speaker,
            text,
        });

        let messageContent = text ?? "";
        let sourcesContent = "";

        const sourcesIndex = messageContent.lastIndexOf("**Sources:**");
        const hasSources = sourcesIndex !== -1;
        const emptyMessage = messageContent.trim() === "" && brainName !== "Quivr" ;

        if (hasSources) {
            sourcesContent = messageContent
                .substring(sourcesIndex + "**Sources:**".length)
                .trim();
            messageContent = messageContent.substring(0, sourcesIndex).trim();
        }

        return (
            <div className={containerWrapperClasses}>
                <div ref={ref} className={containerClasses}>
                    <div className="flex justify-end">
                        <div className="flex items-center gap-2">
                            {!isUserSpeaker && (
                                <>
                                    {hasSources && <SourcesButton sources={sourcesContent}/>}
                                    {emptyMessage && <FaSpinner className="animate-spin text-slate-200"/>}
                                    {!emptyMessage &&
                                        <CopyButton handleCopy={handleCopy} isCopied={isCopied}/>}
                                </>
                            )}
                        </div>
                    </div>
                    <MessageContent
                        text={messageContent}
                        markdownClasses={markdownClasses}
                    />
                </div>
            </div>
        );
    }
);

MessageRow.displayName = "MessageRow";
