import tailwindcss from "@tailwindcss/vite";
import { TanStackRouterVitePlugin } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [
    TanStackRouterVitePlugin(),
    react(),
    tailwindcss(),
    tsconfigPaths(),
  ],
  ssr: {
    external: ["node_modules"],
  },
  build: {
    target: "esnext",
    minify: "terser",
  },
  server: {
    middlewareMode: true,
  },
});
