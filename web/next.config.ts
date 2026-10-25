import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // A self-contained server for the container image (infra/): node server.js, no node_modules.
  output: "standalone",
  cacheComponents: true,
  partialPrefetching: true,
  // Keep the repo free of generated AGENTS.md files.
  agentRules: false,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
