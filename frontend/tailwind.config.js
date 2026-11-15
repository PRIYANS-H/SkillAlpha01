/** @type {import('tailwindcss').Config} */
// Design tokens are CSS variables (defined for light and dark in src/index.css) so the whole
// app themes by toggling the `dark` class on <html>. Use these tokens, not raw hex values.
const token = (name) => `rgb(var(--c-${name}) / <alpha-value>)`;

export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "surface": token("surface"),
        "surface-container-lowest": token("surface-container-lowest"),
        "surface-container-low": token("surface-container-low"),
        "surface-container": token("surface-container"),
        "surface-container-high": token("surface-container-high"),
        "surface-container-highest": token("surface-container-highest"),
        "on-surface": token("on-surface"),
        "on-surface-variant": token("on-surface-variant"),
        "outline": token("outline"),
        "outline-variant": token("outline-variant"),
        "primary": token("primary"),
        "primary-container": token("primary-container"),
        "primary-fixed": token("primary-fixed"),
        "primary-fixed-dim": token("primary-fixed-dim"),
        "on-primary": token("on-primary"),
        "on-primary-fixed": token("on-primary-fixed"),
        "secondary": token("secondary"),
        "secondary-container": token("secondary-container"),
        "secondary-fixed": token("secondary-fixed"),
        "on-secondary-container": token("on-secondary-container"),
        "error": token("error"),
        "error-container": token("error-container"),
        "on-error-container": token("on-error-container"),
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "Inter", "sans-serif"]
      },
      borderRadius: {
        "xl": "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem"
      },
      keyframes: {
        "toast-in": { from: { opacity: "0", transform: "translateY(8px) scale(0.98)" }, to: { opacity: "1", transform: "none" } },
        "fade-up": { from: { opacity: "0", transform: "translateY(6px)" }, to: { opacity: "1", transform: "none" } },
        "pop": { "0%": { transform: "scale(0.6)", opacity: "0" }, "70%": { transform: "scale(1.08)" }, "100%": { transform: "scale(1)", opacity: "1" } }
      },
      animation: {
        "toast-in": "toast-in 180ms ease-out",
        "fade-up": "fade-up 240ms ease-out both",
        "pop": "pop 360ms ease-out both"
      }
    },
  },
  plugins: [],
}
