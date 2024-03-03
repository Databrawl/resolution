import {useQuery, useQueryClient} from "@tanstack/react-query";
import {useParams} from "next/navigation";

import {ONBOARDING_DATA_KEY} from "@/lib/api/onboarding/config";
import {useOnboardingApi} from "@/lib/api/onboarding/useOnboardingApi";

import {Onboarding} from "../types/Onboarding";

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const useOnboarding = () => {
    const params = useParams();
    const {updateOnboarding} = useOnboardingApi();
    const queryClient = useQueryClient();

    // const chatId = params?.chatId as string | undefined;

    // const {data} = useQuery({
    //     queryFn: getOnboarding,
    //     queryKey: [ONBOARDING_DATA_KEY],
    // });

    // REsolution: removed data usage here, using constant value to always show onboarding first
    // const onboarding: Onboarding = data ?? {
    const onboarding: Onboarding = {
        onboarding_a: true,
        onboarding_b1: true,
        onboarding_b2: true,
        onboarding_b3: true,
    };

    const isOnboarding = Object.values(onboarding).some((value) => value);

    const updateOnboardingHandler = async (
        newOnboardingStatus: Partial<Onboarding>
    ) => {
        await updateOnboarding(newOnboardingStatus);
        await queryClient.invalidateQueries({queryKey: [ONBOARDING_DATA_KEY]});
    };

    const shouldDisplayWelcomeChat = onboarding.onboarding_a;

    const shouldDisplayOnboardingAInstructions =
        // REsolution team: we display onboarding always, not just for a new chat
        // chatId === undefined && shouldDisplayWelcomeChat;
        shouldDisplayWelcomeChat;

    // console.log("shouldDisplayOnboardingAInstructions", shouldDisplayOnboardingAInstructions);
    // console.log("chatId", chatId);
    // console.log("shouldDisplayWelcomeChat", shouldDisplayWelcomeChat);

    return {
        onboarding,
        shouldDisplayOnboardingAInstructions,
        shouldDisplayWelcomeChat,
        updateOnboarding: updateOnboardingHandler,
        isOnboarding,
    };
};
