/**
 * Interface for extracted HTML data
 */
export interface HtmlData {
  elements: HtmlElement[];
}

/**
 * Interface for an HTML element
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
 * Interface for a Figma node
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
 * Interface for communication between the extension and the plugin
 */
export interface ExtensionMessage {
  type: string;
  payload: any;
}

/**
 * Interface for extracted interface data
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
