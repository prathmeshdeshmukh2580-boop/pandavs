/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        studio: {
          950: '#030712',
          900: '#0f172a',
          800: '#1e293b',
          700: '#334155',
          600: '#475569',
          accent: '#6366f1',
          emerald: '#10b981',
          amber: '#f59e0b',
        }
      }
    },
  },
  plugins: [],
}
