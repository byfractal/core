import React, { useState, useEffect } from "react";
import { SignIn, useClerk } from "@clerk/clerk-react";
import { ClerkProvider } from "@clerk/clerk-react";

declare global {
  interface Window {
    Clerk?: {
      signOut: () => Promise<void>;
    };
  }
}

// Utiliser process.env au lieu de import.meta.env
const CLERK_PUBLISHABLE_KEY = process.env.VITE_CLERK_PUBLISHABLE_KEY as string;

export function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [pluginMessage, setPluginMessage] = useState(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Écouter les messages de Figma
    window.onmessage = (event) => {
      const message = event.data.pluginMessage;
      setPluginMessage(message);
    };

    // Nettoyer l'écouteur
    return () => {
      window.onmessage = null;
    };
  }, []);

  // Fonction pour envoyer un message à Figma
  const sendToFigma = (type: string, data?: any) => {
    parent.postMessage({ pluginMessage: { type, data } }, "*");
  };

  const handleSignOut = async () => {
    try {
      await window.Clerk?.signOut();
      setIsAuthenticated(false);
      sendToFigma("AUTH_SIGNOUT");
    } catch (err) {
      setError("Erreur lors de la déconnexion");
    }
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
        {error && (
          <div className="absolute top-4 right-4 bg-red-500 text-white px-4 py-2 rounded">
            {error}
          </div>
        )}

        {!isAuthenticated ? (
          <div className="w-full max-w-md p-6">
            <SignIn
              routing="virtual"
              afterSignInUrl="/"
              signUpUrl="/sign-up"
              redirectUrl="/"
            />
          </div>
        ) : (
          <div className="text-center text-white">
            <h2 className="text-xl font-semibold mb-4">HCentric Interface</h2>
            <p className="mb-4">Authentifié avec succès</p>
            <div className="space-y-4">
              <button
                onClick={() => sendToFigma("START_PLUGIN")}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Commencer
              </button>
              <button
                onClick={handleSignOut}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors block w-full"
              >
                Se déconnecter
              </button>
            </div>
          </div>
        )}
      </div>
    </ClerkProvider>
  );
}
