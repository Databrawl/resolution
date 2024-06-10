import React, { useEffect, useState } from 'react';

import { useOnboardingApi } from "@/lib/api/onboarding/useOnboardingApi";

import { MessageRow } from "../QADisplay";

export const Onboarding = (): JSX.Element => {
    const { getOnboardingData } = useOnboardingApi();
    const [greeting, setGreeting] = useState<string | null>(null);

    useEffect(() => {
        const fetchGreeting = async () => {
            const onboardingData = await getOnboardingData();
            setGreeting(onboardingData.greeting);
        };

        void fetchGreeting();
    }, [getOnboardingData]);

    return (
        <div className="flex flex-col gap-2 mb-3">
            {greeting && <MessageRow speaker={"assistant"} brainName={"Quivr"} text={greeting} />}
        </div>
    );
};
