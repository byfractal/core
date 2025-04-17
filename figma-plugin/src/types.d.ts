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

export interface Project {
  id: string;
  name: string;
  description?: string;
  editedAt: string;
  tags?: string[];
}

export interface ProjectCard {
  project: Project;
  onClick?: (project: Project) => void;
}

export interface Optimization {
  id: string;
  title: string;
  description: string;
  impact: "low" | "medium" | "high";
  type: string;
  projectId?: string;
  createdAt?: string;
  tags: SemanticTag[];
  status?: string;
}

export type SemanticTagType =
  | "performance"
  | "accessibility"
  | "ux"
  | "ui"
  | "branding"
  | "error"
  | "warning"
  | "success"
  | "info"
  | "Layout"
  | "Friction"
  | "Navigation"
  | "Conversion"
  | "Performance"
  | "Accessibility"
  | "Mobile"
  | "Desktop";

export interface SemanticTag {
  text?: string;
  type: SemanticTagType;
}
