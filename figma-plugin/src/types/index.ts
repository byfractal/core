/**
 * Project types for the Figma plugin
 */

// Semantic tags for categorizing optimizations
export type SemanticTagType = 
  | 'Layout' 
  | 'Friction' 
  | 'Navigation' 
  | 'Conversion' 
  | 'Performance' 
  | 'Accessibility'
  | 'Mobile'
  | 'Desktop';

// Tag information with type and color
export interface SemanticTag {
  type: SemanticTagType;
  color?: string; // Optional custom color override
}

// Project information
export interface Project {
  id: string;
  name: string;
  createdAt: string; // ISO string
  lastModified: string; // ISO string
  tags: SemanticTag[];
  image?: string; // Optional project thumbnail/icon URL
}

// Optimization information
export interface Optimization {
  id: string;
  projectId: string;
  title: string;
  createdAt: string;
  tags: SemanticTag[];
  status: 'pending' | 'in-progress' | 'completed';
}

// Dropdown menu item
export interface DropdownMenuItem {
  label: string;
  action: () => void;
  icon?: React.ReactNode;
  color?: string;
  disabled?: boolean;
} 