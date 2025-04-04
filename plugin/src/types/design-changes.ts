/**
 * Types standardisés pour représenter les modifications UI
 */

/**
 * Types d'éléments Figma supportés
 */
export type ElementTypeType =
  | "FRAME"
  | "TEXT"
  | "RECTANGLE"
  | "COMPONENT"
  | "INSTANCE"
  | "GROUP";

/**
 * Types d'actions possibles sur les éléments
 */
export type ActionTypeType =
  | "CREATE"
  | "UPDATE"
  | "DELETE"
  | "REPOSITION"
  | "RESIZE"
  | "RECOLOR"
  | "REGROUP";

/**
 * Interface pour les propriétés de style
 */
export interface StylePropertiesInterface {
  fill?: {
    color?: { r: number; g: number; b: number; a?: number };
    type?: "SOLID" | "GRADIENT_LINEAR" | "GRADIENT_RADIAL";
  };
  stroke?: {
    color?: { r: number; g: number; b: number; a?: number };
    weight?: number;
  };
  effects?: Array<{
    type: "DROP_SHADOW" | "INNER_SHADOW" | "BLUR";
    radius?: number;
    color?: { r: number; g: number; b: number; a?: number };
    offset?: { x: number; y: number };
  }>;
  cornerRadius?:
    | number
    | {
        topLeft?: number;
        topRight?: number;
        bottomLeft?: number;
        bottomRight?: number;
      };
  opacity?: number;
}

/**
 * Interface pour les propriétés de texte
 */
export interface TextPropertiesInterface {
  content?: string;
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: number;
  letterSpacing?: number;
  lineHeight?: number | { value: number; unit: "PIXELS" | "PERCENT" };
  textAlign?: "LEFT" | "CENTER" | "RIGHT" | "JUSTIFIED";
  textCase?: "ORIGINAL" | "UPPER" | "LOWER" | "TITLE";
  textDecoration?: "NONE" | "UNDERLINE" | "STRIKETHROUGH";
}

/**
 * Interface pour la position et la taille
 */
export interface LayoutPropertiesInterface {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  rotation?: number;
  constraints?: {
    horizontal: "LEFT" | "RIGHT" | "CENTER" | "SCALE" | "STRETCH";
    vertical: "TOP" | "BOTTOM" | "CENTER" | "SCALE" | "STRETCH";
  };
}

/**
 * Interface pour une modification UI individuelle
 */
export interface DesignChangeInterface {
  id: string;
  targetId?: string; // ID de l'élément à modifier (non requis pour CREATE)
  action: ActionTypeType;
  elementType?: ElementTypeType; // Requis pour CREATE
  properties?: {
    style?: StylePropertiesInterface;
    text?: TextPropertiesInterface;
    layout?: LayoutPropertiesInterface;
  };
  metadata?: {
    reasonForChange: string;
    expectedImprovement: string;
    confidenceScore?: number; // 0-1
    dataPoints?: string[]; // Références aux données utilisées
  };
}

/**
 * Interface pour un ensemble de modifications UI
 */
export interface DesignChangesCollectionInterface {
  id: string;
  title: string;
  description: string;
  changes: DesignChangeInterface[];
  metrics?: {
    expectedImprovementScore: number; // 0-100
    impactAreas: string[];
    priority: "LOW" | "MEDIUM" | "HIGH";
    implementationComplexity: "LOW" | "MEDIUM" | "HIGH";
  };
  timestamp: number;
  version: string;
}
