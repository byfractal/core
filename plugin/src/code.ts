import { ExtensionCommunicationService } from "./services/extension/communication";

/**
 * Point d'entrée du plugin Figma
 */
figma.showUI(__html__, { width: 450, height: 550 });

// Initialisation du service de communication avec l'extension
ExtensionCommunicationService.initialize();

// Gestion des messages de l'interface utilisateur
figma.ui.onmessage = async (msg) => {
  switch (msg.type) {
    case "cancel":
      figma.closePlugin();
      break;

    case "import-html":
      // Notification à l'utilisateur
      figma.notify("Ready to receive HTML interface data");
      break;

    default:
      break;
  }
};

// Message de bienvenue
figma.notify("Plugin initialized and ready to import interfaces");
