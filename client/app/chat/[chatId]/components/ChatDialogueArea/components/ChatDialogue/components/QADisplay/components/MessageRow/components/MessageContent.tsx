import ReactMarkdown from "react-markdown";

export const MessageContent = ({
                                   text,
                                   markdownClasses,
                               }: {
    text: string;
    markdownClasses: string;
}): JSX.Element => {

    return (
        <div data-testid="chat-message-text" className="mt-2">
            <ReactMarkdown className={`text-sm ${markdownClasses}`}>{text}</ReactMarkdown>
        </div>
    );
};
