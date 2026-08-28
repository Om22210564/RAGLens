import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: { colors: { canvas: "#f8fafc", panel: "#ffffff", ink: "#172033", muted: "#5f6b7a", line: "#d9e0ea", accent: "#1456d9", "accent-strong": "#0b3fa8", success: "#087443", warning: "#a45d00", danger: "#b42318" }, boxShadow: { panel: "0 1px 2px rgb(15 23 42 / 0.07)" } } },
  plugins: []
};

export default config;
