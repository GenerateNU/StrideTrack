export const config = {
  apiUrl: import.meta.env.VITE_API_URL,

  development: {
    bypassAuth: import.meta.env.VITE_ENVIRONMENT === "development",
    devTokenKey: "dev-token",
  },
} as const;
