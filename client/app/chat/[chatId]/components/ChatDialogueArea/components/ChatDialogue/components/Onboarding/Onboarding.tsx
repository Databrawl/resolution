import {useOnboardingApi} from "@/lib/api/onboarding/useOnboardingApi";
import {stepsContainerStyle} from "./styles";
import {MessageRow} from "../QADisplay";

export const Onboarding = (): JSX.Element => {
    const {getOnboardingA} = useOnboardingApi();

    const onboardingA = getOnboardingA();

    return (
        <div className="flex flex-col gap-2 mb-3">
            <MessageRow speaker={"assistant"} brainName={"Quivr"}>
                <div className={stepsContainerStyle}>
                    {onboardingA}
                </div>
            </MessageRow>
        </div>
    );
};
