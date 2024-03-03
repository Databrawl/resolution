import {useAxios} from "@/lib/hooks";
import {Onboarding} from "@/lib/types/Onboarding";

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const useOnboardingApi = () => {
    const {axiosInstance} = useAxios();
    const getOnboarding = async () => {
        return {
            onboarding_a: true,
            onboarding_b1: true,
            onboarding_b2: true,
            onboarding_b3: true,
        };
        // return (await axiosInstance.get<Onboarding>("/onboarding")).data;
    };
    const getOnboardingA = () => {
        return "Hello, this is Crypto.com. I am a manager of a top-class Support team. You can do magic with us."
        // TODO: replace with an API call for a given org:
        // return (await axiosInstance.get<Onboarding>("/onboarding")).data;
    };
    const updateOnboarding = async (onboarding: Partial<Onboarding>) => {
        return (await axiosInstance.put<Onboarding>("/onboarding", onboarding))
            .data;
    };

    return {
        getOnboarding,
        getOnboardingA,
        updateOnboarding,
    };
};
