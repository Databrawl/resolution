// components/Login.jsx

import {
    usePasswordAutoLogin
} from "@/app/(home)/components/EmailLogin/components/PasswordLogin/hooks/usePasswordAutoLogin";

const SupaLogin = () => {
    const {handlePasswordAutoLogin} = usePasswordAutoLogin("slack");

    // Directly call the function within the JSX
    void handlePasswordAutoLogin();

    return (
        <div>
            <p></p>
        </div>
    );
};

export default SupaLogin;
