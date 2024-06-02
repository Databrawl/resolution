import {useTranslation} from "react-i18next";

import {useSupabase} from "@/lib/context/SupabaseProvider";
import {useToast} from "@/lib/hooks";

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const usePasswordAutoLogin = (product: string) => {
    const {supabase} = useSupabase();
    const {t} = useTranslation("login");
    const {publish} = useToast();

    let email = '';
    let password = '';

    if (product === 'slack') {
        email = 'slackboy@resolution.bot';
        password = 'SlackMeHard';
    }
    const handlePasswordAutoLogin = async () => {
        if (email === "") {
            publish({
                variant: "danger",
                text: t("errorMailMissed"),
            });

            return;
        }

        if (password === "") {
            publish({
                variant: "danger",
                text: t("errorPasswordMissed"),
            });

            return;
        }

        const {error} = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        if (error) {
            publish({
                variant: "danger",
                text: error.message,
            });

            throw error; // this error is caught by react-hook-form
        }
    };

    return {
        handlePasswordAutoLogin: handlePasswordAutoLogin,
    };
};
