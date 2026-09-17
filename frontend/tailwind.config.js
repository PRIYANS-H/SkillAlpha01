/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "surface": "#f6fbf5",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f0f5ef",
        "surface-container": "#eaefea",
        "surface-container-high": "#e5e9e4",
        "surface-container-highest": "#dfe4de",
        "on-surface": "#181d1a",
        "on-surface-variant": "#404943",
        "outline": "#707973",
        "outline-variant": "#E1E5DF",
        "primary": "#0a4831",
        "primary-container": "#286047",
        "primary-fixed": "#b4f0cf",
        "on-primary": "#ffffff",
        "secondary": "#ae3200",
        "secondary-container": "#FF5B22",
        "secondary-fixed": "#ffdbd0",
        "on-secondary-container": "#521300",
        "error": "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a"
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "Inter", "sans-serif"]
      },
      borderRadius: {
        "xl": "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem"
      }
    },
  },
  plugins: [],
}
