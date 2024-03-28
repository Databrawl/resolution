/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: "class",
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./lib/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            // backgroundImage: {
            //     "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
            //     "gradient-conic":
            //         "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
            // },
            colors: {
                black: "#11243E",
                primary: "#0B7FAB",
                secondary: "#F3ECFF",
                tertiary: "#FFFFFF",
                accent: "#13ABBA",
                highlight: "#FAFAFA",
                "accent-hover": "#11243e",
                "chat-bg-gray": "#FFFFFF",
                "msg-gray": "#0B7FAB",
                "msg-header-gray": "#8F8F8F",
                "msg-purple": "#F2F2F2",
                "onboarding-yellow-bg": "#D8EDF5",
                ivory: "#FFFFFF",
            },
        },
    },
    plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")],
};
