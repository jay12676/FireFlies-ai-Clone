import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Fireflies-inspired indigo/purple accent on neutral grays.
        brand: {
          50: "#eef1ff",
          100: "#e0e5ff",
          200: "#c7cfff",
          300: "#a4afff",
          400: "#8186fb",
          500: "#6c5ce7",
          600: "#5b46d6",
          700: "#4c38b4",
          800: "#3f3092",
          900: "#372d75",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
