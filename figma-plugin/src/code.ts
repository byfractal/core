/// <reference types="@figma/plugin-typings" />


const WIDTH = 450;
const HEIGHT = 650; // 

// Show UI with specified dimensions
figma.showUI(__html__, { 
  width: WIDTH, 
  height: HEIGHT,
  themeColors: true // Use Figma theme colors
});

console.log("Plugin UI launched");

// Sample projects data for demonstration
const demoProjects = [
  {
    id: "proj_001",
    name: "Linear App",
    editedAt: "1 hour ago"
  },
  {
    id: "proj_002",
    name: "Dashboard UI",
    editedAt: "Yesterday" 
  },
  {
    id: "proj_003",
    name: "Mobile App",
    editedAt: "Last week"
  }
];

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
      
      case 'GET_PROJECTS':
        console.log("Projects requested");
        // Send demo projects to UI
        figma.ui.postMessage({
          type: 'PROJECTS_LOADED',
          projects: demoProjects
        });
        break;
        
      case 'SELECT_PROJECT':
        console.log("Project selected:", msg.projectName);
        // Handle project selection - could navigate to project details page
        // For now, just send a message back
        figma.ui.postMessage({
          type: 'PROJECT_SELECTED',
          projectName: msg.projectName
        });
        break;
        
      case 'ADD_PROJECT':
        console.log("Add new project requested");
        // Handle new project creation
        // This would typically open a form or dialog to create a project
        figma.ui.postMessage({
          type: 'SHOW_CREATE_PROJECT'
        });
        break;
        
      case 'ping':
        console.log("Ping received from UI");
        figma.ui.postMessage({ 
          type: 'pong',
          message: 'Pong - connection working!'
        });
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