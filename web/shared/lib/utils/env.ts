export const isDev = process.env.NODE_ENV === "development";
export const isProd = process.env.NODE_ENV === "production";

export const isBrowser = typeof window !== "undefined";

export const getBaseUrl = () => {
    if (isBrowser) return ""; // browser should use relative url
    if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`; // SSR should use vercel url
    return `http://localhost:${process.env.PORT || 3000}`; // dev SSR should use localhost
};
