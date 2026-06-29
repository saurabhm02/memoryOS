import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        surface: { DEFAULT: "var(--surface)", 2: "var(--surface-2)" },
        border: { DEFAULT: "var(--border)", strong: "var(--border-strong)" },
        ink: {
          DEFAULT: "var(--ink)",
          muted: "var(--ink-muted)",
          subtle: "var(--ink-subtle)",
        },
        primary: {
          DEFAULT: "var(--primary)",
          hover: "var(--primary-hover)",
          ink: "var(--primary-ink)",
        },
        "root-cause": { DEFAULT: "var(--root-cause)", bg: "var(--root-cause-bg)" },
        weak: "var(--weak)",
        medium: "var(--medium)",
        mastered: "var(--mastered)",
        unvisited: "var(--unvisited)",
        pattern: "var(--pattern)",
        success: "var(--success)",
        danger: "var(--danger)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      borderRadius: { lg: "10px", md: "8px", sm: "6px" },
      boxShadow: {
        "root-cause": "0 0 0 1px var(--root-cause), 0 0 24px -4px var(--root-cause)",
        panel: "0 1px 0 0 var(--border) inset, 0 8px 24px -12px rgb(0 0 0 / 0.5)",
      },
      keyframes: {
        "fade-in": { from: { opacity: "0" }, to: { opacity: "1" } },
        "rise-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.45" },
        },
      },
      animation: {
        "fade-in": "fade-in 200ms ease-out",
        "rise-in": "rise-in 280ms cubic-bezier(0.16,1,0.3,1)",
        "pulse-soft": "pulse-soft 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [animate],
} satisfies Config;
