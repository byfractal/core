/// <reference types="@figma/plugin-typings" />

// UI Configuration
const WIDTH = 450;
const HEIGHT = 650;

// HTML pages
const HTML_PAGES = {
  PROJECTS: __html__, // Default UI
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
  `,
};

// Current page tracker
let currentPage: "PROJECTS" | "IMPORT" = "PROJECTS";

// Handle command from menu selection
figma.command && handleCommand(figma.command);

function handleCommand(command: string) {
  switch (command) {
    case "projects":
      currentPage = "PROJECTS";
      break;
    case "import":
      currentPage = "IMPORT";
      break;
    default:
      // Default to projects page
      currentPage = "PROJECTS";
  }

  // Show the appropriate UI
  figma.showUI(HTML_PAGES[currentPage], {
    width: WIDTH,
    height: HEIGHT,
    themeColors: true,
  });
}

// If no command is specified, show default UI
if (!figma.command) {
  // Show UI with specified dimensions
  figma.showUI(HTML_PAGES[currentPage], {
    width: WIDTH,
    height: HEIGHT,
    themeColors: true, // Use Figma theme colors
  });
}

console.log("Plugin UI launched");

// Sample projects data for demonstration
const demoProjects = [
  {
    id: "proj_001",
    name: "Linear App",
    editedAt: "1 hour ago",
  },
  {
    id: "proj_002",
    name: "Dashboard UI",
    editedAt: "Yesterday",
  },
  {
    id: "proj_003",
    name: "Mobile App",
    editedAt: "Last week",
  },
];

// Handle messages from the UI
figma.ui.onmessage = (msg) => {
  console.log("Message received from UI:", msg);

  try {
    // Process different message types
    switch (msg.type) {
      case "UI_READY":
        console.log("UI ready - Sending initialization data");
        figma.ui.postMessage({
          type: "INIT_DATA",
          version: "1.0.0",
        });
        break;

      case "GET_PROJECTS":
        console.log("Projects requested");
        // Send demo projects to UI
        figma.ui.postMessage({
          type: "PROJECTS_LOADED",
          projects: demoProjects,
        });
        break;

      case "SELECT_PROJECT":
        console.log("Project selected:", msg.projectName);
        // Handle project selection - could navigate to project details page
        // For now, just send a message back
        figma.ui.postMessage({
          type: "PROJECT_SELECTED",
          projectName: msg.projectName,
        });
        break;

      case "ADD_PROJECT":
        console.log("Add new project requested");

        // Change approach: directly set HTML_PAGES['IMPORT'] instead of sending a message
        currentPage = "IMPORT";
        figma.showUI(HTML_PAGES[currentPage], {
          width: WIDTH,
          height: HEIGHT,
          themeColors: true,
        });
        break;

      case "NAVIGATE_TO_PROJECTS":
        console.log("Navigating back to projects page");
        // Update current page
        currentPage = "PROJECTS";
        figma.showUI(HTML_PAGES[currentPage], {
          width: WIDTH,
          height: HEIGHT,
          themeColors: true,
        });
        break;

      case "IMPORT_DATA":
        console.log(
          "Importing data with API key:",
          msg.apiKey,
          "and date range:",
          msg.dateRange
        );
        // Simulate import process
        setTimeout(() => {
          // Send import started message
          figma.ui.postMessage({
            type: "IMPORT_STARTED",
            importId: "import_" + Date.now(),
          });

          // Simulate import completion after 2 seconds
          setTimeout(() => {
            figma.ui.postMessage({
              type: "IMPORT_COMPLETE",
              importId: "import_" + Date.now(),
            });
          }, 2000);
        }, 1000);
        break;

      case "IMPORT_COMPLETE":
        console.log("Import completed with ID:", msg.importId);
        // Here you would navigate to a results or dashboard page
        figma.notify("Import completed successfully!");
        // For now, navigate back to projects page
        // Update current page
        currentPage = "PROJECTS";
        figma.showUI(HTML_PAGES[currentPage], {
          width: WIDTH,
          height: HEIGHT,
          themeColors: true,
        });
        break;

      case "INSTALL_EXTENSION":
        console.log("Opening browser extension installation page");
        // In a real plugin, you would direct users to the Chrome Web Store
        figma.notify("Would redirect to extension installation page");
        break;

      case "ping":
        console.log("Ping received from UI");
        figma.ui.postMessage({
          type: "pong",
          message: "Pong - connection working!",
        });
        break;

      case "cancel":
        figma.closePlugin();
        break;

      default:
        console.log("Unrecognized message:", msg);
    }
  } catch (error) {
    console.error("Error handling message:", error);
    figma.notify("An error occurred", { error: true });
    figma.ui.postMessage({
      type: "ERROR",
      message: "An error occurred processing your request",
    });
  }
};

import { generateCodeVerifier, generateCodeChallenge } from "./oauth-utils";

type AuthState = {
  isAuthenticated: boolean;
  userId?: string;
  accessToken?: string;
};

// État initial d'authentification
let authState: AuthState = {
  isAuthenticated: false,
};

// Vérifier si l'utilisateur est déjà authentifié
async function checkStoredAuth() {
  try {
    const storedToken = await figma.clientStorage.getAsync("accessToken");
    const storedUserId = await figma.clientStorage.getAsync("userId");

    if (storedToken && storedUserId) {
      authState = {
        isAuthenticated: true,
        userId: storedUserId as string,
        accessToken: storedToken as string,
      };

      // Informer l'UI que l'utilisateur est authentifié
      figma.ui.postMessage({
        type: "AUTH_STATE_CHANGED",
        authState,
      });

      return true;
    }
  } catch (error) {
    console.error("Error checking stored auth:", error);
  }

  return false;
}

// Initialiser le processus d'authentification OAuth avec PKCE
async function initOAuthFlow() {
  try {
    // Générer et stocker code_verifier pour PKCE
    const codeVerifier = generateCodeVerifier();
    await figma.clientStorage.setAsync("codeVerifier", codeVerifier);

    // Générer code_challenge à partir du code_verifier
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    // URL de redirection qui sera gérée par votre serveur ou page web
    const redirectUri = encodeURIComponent(
      "https://votredomaine.com/auth-callback"
    );

    // Construire l'URL d'autorisation avec tous les paramètres nécessaires
    const clerkDomain = "clerk.your-domain.com"; // Remplacez par votre domaine Clerk
    const authUrl =
      `https://${clerkDomain}/oauth/authorize?` +
      `response_type=code` +
      `&client_id=${process.env.CLERK_CLIENT_ID}` +
      `&redirect_uri=${redirectUri}` +
      `&scope=openid profile email` +
      `&code_challenge=${codeChallenge}` +
      `&code_challenge_method=S256` +
      `&state=${generateRandomState()}`;

    // Ouvrir une nouvelle fenêtre pour l'authentification
    figma.showUI(__html__, { width: 400, height: 550 });
    figma.ui.postMessage({ type: "OPEN_AUTH_WINDOW", url: authUrl });
  } catch (error) {
    console.error("Error initializing OAuth flow:", error);
    figma.ui.postMessage({
      type: "AUTH_ERROR",
      message: "Failed to initialize authentication",
    });
  }
}

// Générer un état aléatoire pour prévenir les attaques CSRF
function generateRandomState(): string {
  return (
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15)
  );
}

// Échanger le code d'autorisation contre un token d'accès
async function exchangeCodeForToken(code: string) {
  try {
    // Récupérer le code_verifier stocké précédemment
    const codeVerifier = await figma.clientStorage.getAsync("codeVerifier");

    // URL de redirection (doit correspondre à celle utilisée lors de l'initialisation)
    const redirectUri = encodeURIComponent(
      "https://votredomaine.com/auth-callback"
    );

    // Créer la requête pour échanger le code contre un token
    const response = await fetch(`https://api.clerk.dev/oauth/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body:
        `grant_type=authorization_code` +
        `&client_id=${process.env.CLERK_CLIENT_ID}` +
        `&code_verifier=${codeVerifier}` +
        `&code=${code}` +
        `&redirect_uri=${redirectUri}`,
    });

    if (!response.ok) {
      throw new Error(`Error exchanging code: ${response.statusText}`);
    }

    const tokenData = await response.json();

    // Stocker le token d'accès et les informations de l'utilisateur
    await figma.clientStorage.setAsync("accessToken", tokenData.access_token);

    // Récupérer les infos de l'utilisateur
    const userResponse = await fetch("https://api.clerk.dev/user", {
      headers: {
        Authorization: `Bearer ${tokenData.access_token}`,
      },
    });

    if (!userResponse.ok) {
      throw new Error(`Error fetching user info: ${userResponse.statusText}`);
    }

    const userData = await userResponse.json();
    await figma.clientStorage.setAsync("userId", userData.id);

    // Mettre à jour l'état d'authentification
    authState = {
      isAuthenticated: true,
      userId: userData.id,
      accessToken: tokenData.access_token,
    };

    // Informer l'UI que l'utilisateur est authentifié
    figma.ui.postMessage({
      type: "AUTH_STATE_CHANGED",
      authState,
    });

    return true;
  } catch (error) {
    console.error("Error exchanging code for token:", error);
    figma.ui.postMessage({
      type: "AUTH_ERROR",
      message: "Failed to complete authentication",
    });
    return false;
  }
}

// Déconnexion et suppression des tokens stockés
async function signOut() {
  try {
    await figma.clientStorage.deleteAsync("accessToken");
    await figma.clientStorage.deleteAsync("userId");
    await figma.clientStorage.deleteAsync("codeVerifier");

    authState = {
      isAuthenticated: false,
    };

    figma.ui.postMessage({
      type: "AUTH_STATE_CHANGED",
      authState,
    });

    return true;
  } catch (error) {
    console.error("Error signing out:", error);
    return false;
  }
}

// Initialiser le plugin
figma.showUI(__html__, { width: 400, height: 550 });

// Vérifier si l'utilisateur est déjà authentifié
checkStoredAuth();

// Écouter les messages de l'UI
figma.ui.onmessage = async (msg) => {
  switch (msg.type) {
    case "INIT_AUTH":
      await initOAuthFlow();
      break;

    case "AUTH_CODE_RECEIVED":
      await exchangeCodeForToken(msg.code);
      break;

    case "SIGN_OUT":
      await signOut();
      break;

    case "START_PLUGIN":
      // Logique pour démarrer les fonctionnalités du plugin
      if (authState.isAuthenticated) {
        // Exécuter les fonctionnalités du plugin qui nécessitent une authentification
        figma.ui.postMessage({ type: "PLUGIN_STARTED" });
      } else {
        figma.ui.postMessage({
          type: "AUTH_ERROR",
          message: "Authentication required to use this feature",
        });
      }
      break;

    default:
      console.log("Unknown message type:", msg.type);
  }
};
