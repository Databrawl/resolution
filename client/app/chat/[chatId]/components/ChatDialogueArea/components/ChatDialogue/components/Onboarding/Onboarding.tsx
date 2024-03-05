import {useEffect, useState} from "react";

import {useOnboardingApi} from "@/lib/api/onboarding/useOnboardingApi";

import {stepsContainerStyle} from "./styles";
import {MessageRow} from "../QADisplay";


export const Onboarding = (): JSX.Element => {
    const {getOnboardingData} = useOnboardingApi();
    const [greeting, setGreeting] = useState<string>("");

    useEffect(() => {
        getOnboardingData().then(data => {
            setGreeting(data.greeting);
        }).catch((error) => {
            // Handle any errors that occur during postMessage or updateChatHistory
            console.error("Error retrieving Onboarding data:", error);
        });
    }, [getOnboardingData]);

    return (
        <div className="flex flex-col gap-2 mb-3">
            <MessageRow speaker={"assistant"} brainName={"Quivr"}>
                <div className={stepsContainerStyle}>
                    {greeting}
                </div>
            </MessageRow>
        </div>
    );
};
