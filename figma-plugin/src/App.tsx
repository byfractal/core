import React, { useState, useEffect } from "react";
import { SignIn } from "@clerk/clerk-react";
import { ClerkProvider } from "@clerk/clerk-react";

// Utiliser VITE au lieu de REACT_APP pour les variables d'environnement
const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [pluginMessage, setPluginMessage] = useState(null);

  useEffect(() => {
    // Écouter les messages de Figma
    window.onmessage = (event) => {
      const message = event.data.pluginMessage;
      setPluginMessage(message);
    };
  }, []);

  // Fonction pour envoyer un message à Figma
  const sendToFigma = (type: string, data?: any) => {
    parent.postMessage({ pluginMessage: { type, data } }, "*");
  };

  if (!CLERK_PUBLISHABLE_KEY) {
    return <div>Error: Missing Clerk Publishable Key</div>;
  }

  return (
    <ClerkProvider
      publishableKey={CLERK_PUBLISHABLE_KEY}
      appearance={{
        baseTheme: "dark",
        layout: {
          shimmer: true,
          socialButtonsPlacement: "bottom",
          socialButtonsVariant: "iconButton",
        },
        variables: {
          colorPrimary: "#2563eb",
          colorBackground: "#1e293b",
          colorText: "#f8fafc",
          colorInputBackground: "#334155",
          colorInputText: "#f8fafc",
          fontFamily: "Inter, sans-serif",
        },
        elements: {
          card: {
            boxShadow: "none",
            backgroundColor: "transparent",
          },
          formButtonPrimary: {
            backgroundColor: "#2563eb",
            "&:hover": {
              backgroundColor: "#1d4ed8",
            },
          },
        },
      }}
    >
      <div className="flex items-center justify-center min-h-screen bg-slate-900">
        {!isAuthenticated ? (
          <div className="w-full max-w-md p-6">
            <SignIn
              routing="virtual"
              afterSignInUrl="/"
              onSuccess={(session) => {
                setIsAuthenticated(true);
                // Envoyer le token à Figma
                sendToFigma("AUTH_SUCCESS", {
                  token: session.token,
                  userId: session.user.id,
                });
              }}
            />
          </div>
        ) : (
          <div className="text-center text-white">
            <h2 className="text-xl font-semibold mb-4">HCentric Interface</h2>
            <p className="mb-4">Authentifié avec succès</p>
            <button
              onClick={() => sendToFigma("START_PLUGIN")}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Commencer
            </button>
          </div>
        )}
      </div>
    </ClerkProvider>
  );
}
