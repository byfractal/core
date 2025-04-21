/// <reference types="@figma/plugin-typings" />

// UI Configuration
const WIDTH = 450;
const HEIGHT = 700; 

// Current page tracker
let currentPage = 'ProjectOverviewPage';

// Current project tracker
let currentProject = {
  id: "proj_001",
  name: 'Linear app'
};

// Show UI and initialize
figma.showUI(__html__, { 
  width: WIDTH, 
  height: HEIGHT,
  themeColors: true
});

// Handle command from menu selection
figma.command && handleCommand(figma.command);

function handleCommand(command: string) {
  changePage('ProjectOverviewPage');
}

// Helper function to change pages
function changePage(page: string) {
  currentPage = page;
  figma.ui.postMessage({ type: 'CHANGE_PAGE', page });
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

// Sample optimizations data for demonstration
const demoOptimizations = [
  {
    id: "opt_001",
    name: "Optimization #1",
    date: "03/30/2025",
    tags: ["Layout", "Friction", "Navigation"]
  },
  {
    id: "opt_002",
    name: "Optimization #2",
    date: "03/15/2025",
    tags: ["Color", "Spacing", "Friction"]
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
        
        changePage('ProjectOverviewPage');
        
        figma.ui.postMessage({
          type: 'PROJECT_DETAILS',
          project: currentProject
        });
        
        figma.ui.postMessage({
          type: 'OPTIMIZATIONS_LOADED',
          optimizations: demoOptimizations
        });
        
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
        // Store current project info
        currentProject = {
          id: msg.projectId,
          name: msg.projectName
        };
        
        // Navigate to the project overview page
        changePage('ProjectOverviewPage');
        break;
        
      case 'GET_PROJECT_DETAILS':
        console.log("Project details requested");
        // Send project details
        figma.ui.postMessage({
          type: 'PROJECT_DETAILS',
          project: currentProject
        });
        break;
        
      case 'GET_OPTIMIZATIONS':
        console.log("Optimizations requested");
        // Send demo optimizations
        figma.ui.postMessage({
          type: 'OPTIMIZATIONS_LOADED',
          optimizations: demoOptimizations
        });
        break;
        
      case 'NEW_OPTIMIZATION':
        console.log("New optimization requested for project:", currentProject.name);
        // In a real app, this would initiate a new optimization flow
        figma.notify("Starting a new optimization for " + currentProject.name);
        // Navigate to import page for now
        changePage('ImportPage');
        break;
        
      case 'VIEW_OPTIMIZATION':
        console.log("View optimization requested:", msg.optimizationId);
        // In a real app, this would navigate to a detailed view of the optimization
        figma.notify("Viewing optimization details: " + msg.optimizationId);
        break;
        
      case 'DELETE_PROJECT':
        console.log("Delete project requested:", msg.projectId);
        // In a real app, this would delete the project after confirmation
        figma.notify("Project deleted: " + currentProject.name);
        // Navigate back to projects page
        changePage('ProjectsPage');
        break;
        
      case 'BACK_TO_PROJECTS':
        console.log("Navigating back to projects page");
        // Update current page
        changePage('ProjectsPage');
        break;
        
      case 'ADD_PROJECT':
        console.log("Add new project requested");
        // Navigate to import page
        changePage('ImportPage');
        break;
        
      case 'NAVIGATE_TO_PROJECTS':
        console.log("Navigating back to projects page");
        // Update current page
        changePage('ProjectsPage');
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
        changePage('ProjectsPage');
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