import path from 'path';
import { fileURLToPath } from 'url';
import { createMDX } from 'fumadocs-mdx/next';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const isDev = process.env.NODE_ENV === "development";
const analyzeEnabled = process.env.ANALYZE === "true";

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const nextConfig = {
    experimental: {
        optimizePackageImports: [
            "lucide-react", "recharts", "framer-motion", "date-fns", "moment", "lodash",
            "clsx", "tailwind-merge", "input-otp", "jose", "bcryptjs", "@radix-ui/react-checkbox",
            "@radix-ui/react-label", "@radix-ui/react-radio-group", "@radix-ui/react-select",
            "@radix-ui/react-slot", "@radix-ui/react-switch", "@radix-ui/react-toggle", "@radix-ui/react-tooltip",
            "react-katex", "katex"
        ],
    },
    reactStrictMode: true,
    typescript: { ignoreBuildErrors: true },
    images: { formats: ["image/webp", "image/avif"] },
    poweredByHeader: false,
    output: 'standalone',
    outputFileTracingRoot: path.join(__dirname, './'),
};

if (!isDev || analyzeEnabled) {
    nextConfig.webpack = (config, { isServer }) => {
        if (!isServer) {
            config.externals = config.externals || [];
            config.externals.push({ "@prisma/client": "commonjs @prisma/client" });
            config.optimization = {
                ...config.optimization,
                usedExports: true,
                sideEffects: false,
                splitChunks: {
                    chunks: "all",
                    cacheGroups: {
                        react: { test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/, name: "react", chunks: "all", priority: 30 },
                        nextjs: { test: /[\\/]node_modules[\\/]next[\\/]/, name: "nextjs", chunks: "all", priority: 25 },
                        vendor: { test: /[\\/]node_modules[\\/]/, name: "vendors", chunks: "all", priority: 10, maxSize: 400000 },
                    },
                },
            };
        }
        return config;
    };
}

let finalConfig = withMDX(nextConfig);

if (analyzeEnabled) {
    const bundleAnalyzer = (await import('@next/bundle-analyzer')).default;
    finalConfig = bundleAnalyzer({ enabled: true })(finalConfig);
}

export default finalConfig;
