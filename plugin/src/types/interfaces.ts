/**
 * Interface pour les données HTML extraites
 */
export interface HtmlData {
  elements: HtmlElement[];
}

/**
 * Interface pour un élément HTML
 */
export interface HtmlElement {
  id: string;
  tagName: string;
  className: string;
  style: any;
  attributes: Record<string, string>;
  children?: HtmlElement[];
}

/**
 * Interface pour un nœud Figma
 */
export interface FigmaNode {
  id: string;
  name: string;
  type: string;
  style: any;
  metadata: {
    sourceId: string;
    className: string;
    tagName: string;
    attributes: Record<string, string>;
  };
  children: FigmaNode[];
}

/**
 * Interface pour la communication entre l'extension et le plugin
 */
export interface ExtensionMessage {
  type: string;
  payload: any;
}

/**
 * Interface pour les données d'interface extraites
 */
export interface ExtractedInterface {
  html: HtmlData;
  metadata: {
    title: string;
    url: string;
    timestamp: number;
    hierarchy: any;
  };
}
