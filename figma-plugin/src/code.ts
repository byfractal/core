/// <reference types="@figma/plugin-typings" />

// Hauteur et largeur du plugin - ajuster selon les besoins
const WIDTH = 400;
const HEIGHT = 600;

// Afficher l'UI avec les dimensions spécifiées
figma.showUI(__html__, { 
  width: WIDTH, 
  height: HEIGHT,
  themeColors: true // Utiliser les couleurs du thème Figma
});

console.log("Plugin UI lancée");

// Gérer les messages de l'UI
figma.ui.onmessage = (msg) => {
  console.log("Message reçu de l'UI:", msg);
  
  // Traiter les différents types de messages
  switch (msg.type) {
    case 'UI_READY':
      console.log("UI prête - Envoi de données d'initialisation");
      figma.ui.postMessage({ 
        type: 'INIT_DATA',
        version: '1.0.0'
      });
      break;
      
    case 'login':
      console.log("Tentative de connexion:", msg.email);
      
      // Simuler authentification réussie
      setTimeout(() => {
        figma.ui.postMessage({
          type: 'LOGIN_RESPONSE',
          success: true
        });
      }, 800);
      break;
      
    case 'cancel':
      figma.closePlugin();
      break;
      
    default:
      console.log("Message non reconnu:", msg);
  }
}; 