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

    switch (product) {
        case 'slack':
        email = 'slackboy@resolution.bot';
        password = 'SlackMeHard';
            break;
        case 'notion':
            email = 'notionhero@resolution.bot';
            password = 'NoteMeDown';
            break;
        case 'github':
            email = 'gitmaster@resolution.bot';
            password = 'RebaseAllTheWay';
            break;
        case 'resolution':
            email = 'reso@resolution.bot';
            password = 'Reso1sTheBest';
            break;
        default:
            // Handle the case where product doesn't match any case
            break;
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
