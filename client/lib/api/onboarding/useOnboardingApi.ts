import {useAxios} from "@/lib/hooks";
import {Onboarding, OnboardingData} from "@/lib/types/Onboarding";

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
    };
    // const getOnboardingA = async () => {
    const getOnboardingData = async () => {
        return (await axiosInstance.get<OnboardingData>("/onboarding")).data;
    };
    const updateOnboarding = async (onboarding: Partial<Onboarding>) => {
        return (await axiosInstance.put<Onboarding>("/onboarding", onboarding))
            .data;
    };

    return {
        getOnboarding,
        getOnboardingData: getOnboardingData,
        updateOnboarding,
    };
};
