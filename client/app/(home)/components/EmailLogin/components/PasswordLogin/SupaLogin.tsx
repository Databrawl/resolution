import {ReactElement} from "react";

import {
    usePasswordAutoLogin
} from "@/app/(home)/components/EmailLogin/components/PasswordLogin/hooks/usePasswordAutoLogin";

interface SupaLoginProps {
    product: string;
}

const SupaLogin = (loginProps: SupaLoginProps): ReactElement => {
    const {handlePasswordAutoLogin} = usePasswordAutoLogin(loginProps.product);

    // Directly call the function within the JSX
    void handlePasswordAutoLogin();

    return (
        <div>
            <p></p>
        </div>
    );
};

export default SupaLogin;
