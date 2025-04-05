import { htmlToFigma } from "@builder.io/html-to-figma";
import { FigmaNode, HtmlData } from "../../types/interfaces";

/**
 * Converts HTML data to Figma elements
 * Preserves the hierarchical structure of elements
 */
export class HtmlToFigmaConverter {
  /**
   * Converts HTML data to Figma elements
   * @param htmlData The extracted HTML data
   * @returns The generated Figma nodes
   */
  public static convert(htmlData: HtmlData): FigmaNode[] {
    try {
      // Utilisez la bibliothèque BuilderIO
      const result = htmlToFigma(htmlData.html);

      // Convertir le résultat au format attendu par votre application
      return this.adaptBuilderIOResult(result);
    } catch (error) {
      console.error("Error converting HTML to Figma:", error);
      return [];
    }
  }

  /**
   * Transform HTML data to Figma nodes
   * @param htmlData The HTML data
   * @returns The Figma nodes
   */
  private static transformHtmlToFigma(htmlData: HtmlData): FigmaNode[] {
    const nodes: FigmaNode[] = [];

    // Loop through each HTML element
    htmlData.elements.forEach((element) => {
      // Create the corresponding Figma node
      const figmaNode = this.createFigmaNode(element);

      // Process children if present
      if (element.children && element.children.length > 0) {
        figmaNode.children = this.transformHtmlToFigma({
          elements: element.children,
        });
      }

      nodes.push(figmaNode);
    });

    return nodes;
  }

  /**
   * Create a Figma node from an HTML element
   * @param element The HTML element
   * @returns The corresponding Figma node
   */
  private static createFigmaNode(element: any): FigmaNode {
    // Convert HTML properties to Figma properties
    const node: FigmaNode = {
      id: element.id || "",
      name: element.tagName || "Frame",
      type: this.mapHtmlTypeToFigma(element.tagName),
      // Convert CSS styles to Figma styles
      style: this.convertCssToFigmaStyle(element.style),
      // Preserve metadata for traceability
      metadata: {
        sourceId: element.id,
        className: element.className,
        tagName: element.tagName,
        attributes: element.attributes,
      },
      children: [],
    };

    return node;
  }

  /**
   * Map HTML types to appropriate Figma types
   * @param htmlType The HTML type
   * @returns The corresponding Figma type
   */
  private static mapHtmlTypeToFigma(htmlType: string): string {
    // Mapping of HTML types to Figma
    const typeMap: { [key: string]: string } = {
      div: "FRAME",
      span: "TEXT",
      p: "TEXT",
      h1: "TEXT",
      h2: "TEXT",
      h3: "TEXT",
      h4: "TEXT",
      h5: "TEXT",
      h6: "TEXT",
      img: "RECTANGLE",
      button: "RECTANGLE",
      input: "RECTANGLE",
      a: "TEXT",
    };

    return typeMap[htmlType.toLowerCase()] || "FRAME";
  }

  /**
   * Convert CSS styles to Figma styles
   * @param cssStyle The CSS styles
   * @returns The Figma styles
   */
  private static convertCssToFigmaStyle(cssStyle: any): any {
    // Convert CSS properties to Figma properties
    return {
      width: cssStyle.width,
      height: cssStyle.height,
      fillColor: cssStyle.backgroundColor,
      textColor: cssStyle.color,
      fontSize: cssStyle.fontSize,
      fontFamily: cssStyle.fontFamily,
      padding: {
        top: cssStyle.paddingTop,
        right: cssStyle.paddingRight,
        bottom: cssStyle.paddingBottom,
        left: cssStyle.paddingLeft,
      },
      margin: {
        top: cssStyle.marginTop,
        right: cssStyle.marginRight,
        bottom: cssStyle.marginBottom,
        left: cssStyle.marginLeft,
      },
      borderRadius: cssStyle.borderRadius,
    };
  }

  // Fonction pour adapter le résultat BuilderIO à votre format
  private static adaptBuilderIOResult(builderResult: any): FigmaNode[] {
    // Implémentation d'adaptation ici
    // ...

    // Pour l'instant, retournez un cadre vide
    return [
      {
        id: "root",
        name: "Converted from HTML",
        type: "FRAME",
        style: {},
        metadata: {
          sourceId: "",
          className: "",
          tagName: "div",
          attributes: {},
        },
        children: [],
      },
    ];
  }
}
