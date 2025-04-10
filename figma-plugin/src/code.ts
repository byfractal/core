/// <reference types="@figma/plugin-typings" />

// Plugin window dimensions - ajusté selon la maquette
const WIDTH = 400;
const HEIGHT = 800; // Hauteur augmentée pour mieux correspondre à la maquette

// Show UI with specified dimensions
figma.showUI(__html__, { 
  width: WIDTH, 
  height: HEIGHT,
  themeColors: true // Use Figma theme colors
});

console.log("Plugin UI launched");

// Handle messages from the UI
figma.ui.onmessage = (msg) => {
  console.log("Message received from UI:", msg);
  
  try {
    // Process different message types
    switch (msg.type) {
      case 'UI_READY':
        console.log("UI ready - Sending initialization data");
        figma.ui.postMessage({ 
          type: 'INIT_DATA',
          version: '1.0.0'
        });
        break;
      
      case 'ping':
        console.log("Ping received from UI");
        figma.ui.postMessage({ 
          type: 'pong',
          message: 'Pong - connection working!'
        });
        break;
        
      case 'login':
        console.log("Login attempt:", msg.email);
        
        // Simulate successful authentication (replace with actual auth logic later)
        setTimeout(() => {
          figma.ui.postMessage({
            type: 'LOGIN_RESPONSE',
            success: true,
            userData: {
              name: 'User Name',
              email: msg.email
            }
          });
          
          // After successful login, you could perform additional actions:
          // - Load user projects
          // - Show main interface
          // - etc.
        }, 800);
        break;
        
      case 'cancel':
        figma.closePlugin();
        break;
        
      default:
        console.log("Unrecognized message:", msg);
    }
  } catch (error) {
    console.error("Error handling message:", error);
    figma.notify("An error occurred", { error: true });
    figma.ui.postMessage({
      type: 'ERROR',
      message: 'An error occurred processing your request'
    });
  }
}; 