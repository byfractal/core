/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_CLERK_PUBLISHABLE_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface ClerkSession {
  token: string;
  user: {
    id: string;
    [key: string]: any;
  };
}
