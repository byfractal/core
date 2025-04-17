import React, { useState, useEffect, useCallback } from "react";
import { createRoot } from "react-dom/client";
import { parseUrlParams } from "./oauth-utils";

interface AuthState {
  isAuthenticated: boolean;
  userId?: string;
  accessToken?: string;
}

function App() {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authWindow, setAuthWindow] = useState<Window | null>(null);

  // Vérifier périodiquement si la fenêtre d'authentification est fermée
  useEffect(() => {
    let checkInterval: number | null = null;

    if (authWindow) {
      checkInterval = window.setInterval(() => {
        if (authWindow.closed) {
          // La fenêtre a été fermée sans compléter l'authentification
          setAuthWindow(null);
          window.clearInterval(checkInterval!);
          setError("Authentication window was closed before completion");
        }
      }, 1000);
    }

    return () => {
      if (checkInterval) {
        window.clearInterval(checkInterval);
      }
    };
  }, [authWindow]);

  // Fonction pour ouvrir la fenêtre d'authentification
  const openAuthWindow = useCallback((url: string) => {
    // Définir les dimensions et position de la fenêtre d'authentification
    const width = 600;
    const height = 700;
    const left = window.screenX + (window.outerWidth - width) / 2;
    const top = window.screenY + (window.outerHeight - height) / 2;

    const authWindowInstance = window.open(
      url,
      "Clerk Auth",
      `width=${width},height=${height},left=${left},top=${top},resizable,scrollbars=yes,status=1`
    );

    if (!authWindowInstance) {
      setError(
        "Could not open authentication window. Please allow popups for this site."
      );
      return;
    }

    setAuthWindow(authWindowInstance);

    // Configurer un écouteur d'événements pour recevoir le code d'autorisation
    window.addEventListener("message", handleAuthCallback);
  }, []);

  // Gérer le callback d'authentification
  const handleAuthCallback = useCallback(
    (event: MessageEvent) => {
      // Vérifier que le message provient de notre page de callback
      if (event.origin !== "https://votredomaine.com") {
        return;
      }

      // Analyser l'URL pour extraire le code d'authentification
      const data = event.data;
      if (data && data.type === "AUTH_CALLBACK") {
        const params = parseUrlParams(data.url);

        if (params.code) {
          // Envoyer le code au plugin pour échange contre un token
          parent.postMessage(
            {
              pluginMessage: {
                type: "AUTH_CODE_RECEIVED",
                code: params.code,
              },
            },
            "*"
          );

          // Fermer la fenêtre d'authentification
          if (authWindow) {
            authWindow.close();
            setAuthWindow(null);
          }

          // Supprimer l'écouteur d'événements
          window.removeEventListener("message", handleAuthCallback);
        }

        if (params.error) {
          setError(
            `Authentication failed: ${params.error_description || params.error}`
          );

          if (authWindow) {
            authWindow.close();
            setAuthWindow(null);
          }

          window.removeEventListener("message", handleAuthCallback);
        }
      }
    },
    [authWindow]
  );

  // Écouter les messages du plugin
  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const message = event.data.pluginMessage;

      if (!message) return;

      switch (message.type) {
        case "AUTH_STATE_CHANGED":
          setAuthState(message.authState);
          setIsLoading(false);
          break;

        case "OPEN_AUTH_WINDOW":
          openAuthWindow(message.url);
          break;

        case "AUTH_ERROR":
          setError(message.message);
          setIsLoading(false);
          break;

        case "PLUGIN_STARTED":
          // Gérer l'état quand le plugin est démarré
          setIsLoading(false);
          break;
      }
    }

    window.addEventListener("message", onMessage);
    setIsLoading(false);

    // Demander l'état d'authentification actuel
    parent.postMessage({ pluginMessage: { type: "GET_AUTH_STATE" } }, "*");

    return () => {
      window.removeEventListener("message", onMessage);
    };
  }, [openAuthWindow]);

  const handleLogin = () => {
    setIsLoading(true);
    setError(null);
    // Demander au plugin d'initialiser le processus d'authentification
    parent.postMessage({ pluginMessage: { type: "INIT_AUTH" } }, "*");
  };

  const handleSignOut = () => {
    setIsLoading(true);
    // Demander au plugin de se déconnecter
    parent.postMessage({ pluginMessage: { type: "SIGN_OUT" } }, "*");
  };

  const handleStartPlugin = () => {
    setIsLoading(true);
    // Demander au plugin de démarrer ses fonctionnalités
    parent.postMessage({ pluginMessage: { type: "START_PLUGIN" } }, "*");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-900 p-4 text-white">
      {error && (
        <div className="absolute top-4 w-full px-4">
          <div className="bg-red-500 text-white p-3 rounded shadow-lg">
            {error}
            <button className="ml-2 font-bold" onClick={() => setError(null)}>
              ×
            </button>
          </div>
        </div>
      )}

      <div className="w-full max-w-md">
        {!authState.isAuthenticated ? (
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Authentication Required</h2>
            <p className="mb-6">Please sign in to use this plugin</p>
            <button
              onClick={handleLogin}
              className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
            >
              Sign In with Clerk
            </button>
          </div>
        ) : (
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Welcome</h2>
            <p className="mb-6">
              You are signed in as User ID: {authState.userId}
            </p>

            <div className="space-y-4">
              <button
                onClick={handleStartPlugin}
                className="w-full py-3 px-4 bg-green-600 hover:bg-green-700 rounded-md transition-colors"
              >
                Start Plugin
              </button>

              <button
                onClick={handleSignOut}
                className="w-full py-3 px-4 bg-red-600 hover:bg-red-700 rounded-md transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Monter l'application React
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("app");
  if (container) {
    const root = createRoot(container);
    root.render(<App />);
  }
});
