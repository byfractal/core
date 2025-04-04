import { ExtensionMessage, ExtractedInterface } from "../../types/interfaces";
import { HtmlToFigmaConverter } from "../../figma/converters/html-to-figma";

/**
 * Service pour gérer la communication avec l'extension Chrome
 */
export class ExtensionCommunicationService {
  /**
   * Initialise les écouteurs de messages
   */
  public static initialize(): void {
    // Écouteur pour les messages de l'extension
    window.addEventListener("message", this.handleMessage);
  }

  /**
   * Gère les messages reçus de l'extension
   * @param event L'événement de message
   */
  private static handleMessage(event: MessageEvent): void {
    // Vérification de l'origine et du type de message
    if (event.data.pluginMessage) {
      const message = event.data.pluginMessage as ExtensionMessage;

      // Traitement en fonction du type de message
      switch (message.type) {
        case "EXTRACTED_INTERFACE":
          ExtensionCommunicationService.processExtractedInterface(
            message.payload
          );
          break;
        case "CONNECTION_ESTABLISHED":
          console.log("Connection established with Chrome extension");
          break;
        default:
          console.warn("Unknown message type:", message.type);
      }
    }
  }

  /**
   * Traite les données d'interface extraites
   * @param data Les données d'interface extraites
   */
  private static processExtractedInterface(data: ExtractedInterface): void {
    try {
      // Conversion des données HTML en nœuds Figma
      const figmaNodes = HtmlToFigmaConverter.convert(data.html);

      // Création d'un frame Figma pour contenir les nœuds
      const frameNode = figma.createFrame();
      frameNode.name = data.metadata.title || "Extracted Interface";

      // Ajout des nœuds Figma au frame
      this.addNodesToParent(figmaNodes, frameNode);

      // Notification de réussite
      figma.notify("Interface successfully converted to Figma");
    } catch (error) {
      console.error("Error processing extracted interface:", error);
      figma.notify("Error processing extracted interface", { error: true });
    }
  }

  /**
   * Ajoute récursivement les nœuds Figma à un parent
   * @param nodes Les nœuds Figma à ajouter
   * @param parent Le nœud parent
   */
  private static addNodesToParent(nodes: any[], parent: any): void {
    nodes.forEach((nodeData) => {
      // Création du nœud Figma en fonction du type
      let node;

      switch (nodeData.type) {
        case "FRAME":
          node = figma.createFrame();
          break;
        case "TEXT":
          node = figma.createText();
          break;
        case "RECTANGLE":
          node = figma.createRectangle();
          break;
        default:
          node = figma.createFrame();
      }

      // Configuration des propriétés de base
      node.name = nodeData.name;

      // Application des styles
      this.applyStyles(node, nodeData.style);

      // Ajout au parent
      parent.appendChild(node);

      // Traitement récursif des enfants
      if (nodeData.children && nodeData.children.length > 0) {
        this.addNodesToParent(nodeData.children, node);
      }
    });
  }

  /**
   * Applique les styles à un nœud Figma
   * @param node Le nœud Figma
   * @param style Les styles à appliquer
   */
  private static applyStyles(node: any, style: any): void {
    // Dimensions
    if (style.width) node.resize(style.width, node.height);
    if (style.height) node.resize(node.width, style.height);

    // Couleurs
    if (style.fillColor && node.fills) {
      node.fills = [{ type: "SOLID", color: this.hexToRgb(style.fillColor) }];
    }

    // Texte
    if (node.type === "TEXT") {
      if (style.textColor) {
        node.fills = [{ type: "SOLID", color: this.hexToRgb(style.textColor) }];
      }

      if (style.fontSize) {
        node.fontSize = style.fontSize;
      }

      if (style.fontFamily) {
        // Chargement de la police si disponible
        figma
          .loadFontAsync({ family: style.fontFamily, style: "Regular" })
          .then(() => {
            node.fontName = { family: style.fontFamily, style: "Regular" };
          })
          .catch(() => {
            console.warn(`Font ${style.fontFamily} not available`);
          });
      }
    }

    // Bordures arrondies
    if (style.borderRadius && "cornerRadius" in node) {
      node.cornerRadius = style.borderRadius;
    }
  }

  /**
   * Convertit une couleur hexadécimale en RGB
   * @param hex La couleur hexadécimale
   * @returns L'objet de couleur RGB
   */
  private static hexToRgb(hex: string): { r: number; g: number; b: number } {
    // Suppression du # si présent
    hex = hex.replace(/^#/, "");

    // Parsing de la couleur hex
    const bigint = parseInt(hex, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;

    // Normalisation pour Figma (0-1)
    return {
      r: r / 255,
      g: g / 255,
      b: b / 255,
    };
  }
}
