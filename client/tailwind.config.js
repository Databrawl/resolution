const plugin = require('tailwindcss/plugin');


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
                primary: "#00ADB5",
                "primary-hover": "#007479",
                secondary: "#1cf700",
                tertiary: "#2a2735",  // chat background
                accent: "#13ABBA",
                highlight: "#414050",
                "accent-hover": "#11243e",
                "chat-bg-gray": "#2a2735",
                "msg-gray": "#00adb5",
                "msg-header-gray": "#8F8F8F",
                "msg-purple": "#46445b",
                "input-back": "#414050",
                "input-text": "#abb4bc",
                "onboarding-yellow-bg": "#D8EDF5",
                ivory: "#2a2735",
                "text-black": "#e6e6e6",
            },
        },
    },
    plugins: [
        require("@tailwindcss/typography"),
        require("@tailwindcss/forms"),
        plugin(function({ addUtilities }) {
      addUtilities({
        'strong': {
          color: '#ff0000', // Change this to your desired color
        },
      });
    })
    ],
};
