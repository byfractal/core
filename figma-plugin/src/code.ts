/// <reference types="@figma/plugin-typings" />

// UI Configuration
const WIDTH = 450;
const HEIGHT = 650; 

// HTML pages
const HTML_PAGES = {
  PROJECTS: __html__,  // Default UI
  IMPORT: `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Import Project</title>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      height: 100%;
      width: 100%;
      overflow: hidden;
    }
    iframe {
      border: none;
      width: 100%;
      height: 100%;
    }
  </style>
</head>
<body>
  <iframe src="./src/ui/ImportPage.html"></iframe>
</body>
</html>
  `
};

// Current page tracker
let currentPage: 'PROJECTS' | 'IMPORT' = 'PROJECTS';

// Handle command from menu selection
figma.command && handleCommand(figma.command);

function handleCommand(command: string) {
  switch (command) {
    case 'projects':
      currentPage = 'PROJECTS';
      break;
    case 'import':
      currentPage = 'IMPORT';
      break;
    default:
      // Default to projects page
      currentPage = 'PROJECTS';
  }
  
  // Show the appropriate UI
  figma.showUI(HTML_PAGES[currentPage], { 
    width: WIDTH, 
    height: HEIGHT,
    themeColors: true
  });
}

// If no command is specified, show default UI
if (!figma.command) {
  // Show UI with specified dimensions
  figma.showUI(HTML_PAGES[currentPage], { 
    width: WIDTH, 
    height: HEIGHT,
    themeColors: true // Use Figma theme colors
  });
}

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
        
        // Change approach: directly set HTML_PAGES['IMPORT'] instead of sending a message
        currentPage = 'IMPORT';
        figma.showUI(HTML_PAGES[currentPage], { 
          width: WIDTH, 
          height: HEIGHT,
          themeColors: true
        });
        break;
        
      case 'NAVIGATE_TO_PROJECTS':
        console.log("Navigating back to projects page");
        // Update current page
        currentPage = 'PROJECTS';
        figma.showUI(HTML_PAGES[currentPage], { 
          width: WIDTH, 
          height: HEIGHT,
          themeColors: true
        });
        break;
        
      case 'IMPORT_DATA':
        console.log("Importing data with API key:", msg.apiKey, "and date range:", msg.dateRange);
        // Simulate import process
        setTimeout(() => {
          // Send import started message
          figma.ui.postMessage({
            type: 'IMPORT_STARTED',
            importId: 'import_' + Date.now()
          });
          
          // Simulate import completion after 2 seconds
          setTimeout(() => {
            figma.ui.postMessage({
              type: 'IMPORT_COMPLETE',
              importId: 'import_' + Date.now()
            });
          }, 2000);
        }, 1000);
        break;
        
      case 'IMPORT_COMPLETE':
        console.log("Import completed with ID:", msg.importId);
        // Here you would navigate to a results or dashboard page
        figma.notify("Import completed successfully!");
        // For now, navigate back to projects page
        // Update current page
        currentPage = 'PROJECTS';
        figma.showUI(HTML_PAGES[currentPage], { 
          width: WIDTH, 
          height: HEIGHT,
          themeColors: true
        });
        break;
        
      case 'INSTALL_EXTENSION':
        console.log("Opening browser extension installation page");
        // In a real plugin, you would direct users to the Chrome Web Store
        figma.notify("Would redirect to extension installation page");
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