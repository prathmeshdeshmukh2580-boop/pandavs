/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      colors: {
        ink: { 950: "#07080f", 900: "#0d1020", 800: "#151a30" },
        verified: "#34d399",
        warn: "#fbbf24",
        danger: "#f87171",
      },
    },
  },
  plugins: [],
};
