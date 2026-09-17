/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#09090b",
        foreground: "#fafafa",
        card: "#121215",
        "card-border": "#27272a",
        muted: "#71717a",
        "muted-dark": "#3f3f46",
        border: "#27272a",
        hover: "#18181b",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "SF Pro Display",
          "SF Pro Text",
          "Inter",
          "Segoe UI",
          "sans-serif"
        ]
      }
    },
  },
  plugins: [],
}

