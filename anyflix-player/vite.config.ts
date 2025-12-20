import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import legacy from "@vitejs/plugin-legacy";
import path from "path";
import { componentTagger } from "lovable-tagger";
import fs from "fs";

// Plugin to copy webOS files to dist
const copyWebOSFiles = () => ({
  name: "copy-webos-files",
  writeBundle() {
    const filesToCopy = ["appinfo.json", "icon.png"];
    filesToCopy.forEach((file) => {
      const src = path.resolve(__dirname, file);
      const dest = path.resolve(__dirname, "dist", file);
      if (fs.existsSync(src)) {
        fs.copyFileSync(src, dest);
        console.log(`✓ Copied ${file} to dist/`);
      }
    });
  },
});

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  base: './',
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    legacy({
      targets: ['chrome 79'],
      modernPolyfills: true,
    }),
    mode === 'development' &&
    componentTagger(),
    copyWebOSFiles(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    target: ["chrome79"],
  },
  esbuild: {
    target: "chrome79",
  },
}));
