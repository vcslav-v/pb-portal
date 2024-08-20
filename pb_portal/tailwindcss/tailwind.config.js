/** @type {import("tailwindcss").Config} */
module.exports = {
  content: ["../templates/**/*.html", "../static/js/**/*.js"],
  theme: {
    extend: {
      fontFamily: {
          sans: ["Helvetica Neue", "ui-sans-serif", "system-ui"],
          serif: ["Georgia", "ui-serif", "serif"],
          mono: ["Menlo", "ui-monospace", "monospace"],
        },
        keyframes: {
          shake: {
            "0%": { transform: "translateX(0)" },
            "10%": { transform: "translateX(-4px)" },
            "20%": { transform: "translateX(4px)" },
            "30%": { transform: "translateX(-4px)" },
            "40%": { transform: "translateX(4px)" },
            "50%": { transform: "translateX(-4px)" },
            "60%": { transform: "translateX(4px)" },
            "70%": { transform: "translateX(-4px)" },
            "80%": { transform: "translateX(4px)" },
            "90%": { transform: "translateX(-4px)" },
            "100%": { transform: "translateX(0)" },
          }
        },
        animation: {
          shake: "shake 0.5s",
        },
    }
  },
  plugins: [],
}