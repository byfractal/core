import { FigmaNode, HtmlData } from "../../types/interfaces";

/**
 * Convertit les données HTML en éléments Figma
 * Préserve la structure hiérarchique des éléments
 */
export class HtmlToFigmaConverter {
  /**
   * Convertit les données HTML en éléments Figma
   * @param htmlData Les données HTML extraites
   * @returns Les nœuds Figma générés
   */
  public static convert(htmlData: HtmlData): FigmaNode[] {
    // Transformation des données HTML en nœuds Figma
    const figmaNodes = this.transformHtmlToFigma(htmlData);
    return figmaNodes;
  }

  /**
   * Transforme récursivement les éléments HTML en nœuds Figma
   * @param htmlData Les données HTML
   * @returns Les nœuds Figma
   */
  private static transformHtmlToFigma(htmlData: HtmlData): FigmaNode[] {
    const nodes: FigmaNode[] = [];

    // Parcours de chaque élément HTML
    htmlData.elements.forEach((element) => {
      // Création du nœud Figma correspondant
      const figmaNode = this.createFigmaNode(element);

      // Traitement des enfants si présents
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
   * Crée un nœud Figma à partir d'un élément HTML
   * @param element L'élément HTML
   * @returns Le nœud Figma correspondant
   */
  private static createFigmaNode(element: any): FigmaNode {
    // Conversion des propriétés HTML en propriétés Figma
    const node: FigmaNode = {
      id: element.id || "",
      name: element.tagName || "Frame",
      type: this.mapHtmlTypeToFigma(element.tagName),
      // Conversion des styles CSS en styles Figma
      style: this.convertCssToFigmaStyle(element.style),
      // Conservation des métadonnées pour la traçabilité
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
   * Mappe les types HTML vers les types Figma appropriés
   * @param htmlType Le type HTML
   * @returns Le type Figma correspondant
   */
  private static mapHtmlTypeToFigma(htmlType: string): string {
    // Mapping des types HTML vers Figma
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
   * Convertit les styles CSS en styles Figma
   * @param cssStyle Les styles CSS
   * @returns Les styles Figma
   */
  private static convertCssToFigmaStyle(cssStyle: any): any {
    // Conversion des propriétés CSS en propriétés Figma
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
}
