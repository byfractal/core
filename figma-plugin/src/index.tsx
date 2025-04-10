import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

// Attendre que le DOM soit complètement chargé
document.addEventListener('DOMContentLoaded', () => {
  // Récupérer l'élément app et vérifier qu'il existe
  const app = document.getElementById('app');
  if (!app) {
    console.error("L'élément #app n'a pas été trouvé");
    return;
  }

  // Note: Nous utilisons maintenant directement ProjectsPage.html via iframe
  // donc ce fichier React n'est pas activement utilisé pour le moment
  
  // Initialiser React (pour future utilisation)
  const root = createRoot(app);
  root.render(
    <React.StrictMode>
      <div className="flex items-center justify-center min-h-screen bg-white">
        <div>Interface HCentric</div>
      </div>
    </React.StrictMode>
  );

  // Notifier le plugin que l'UI est prête via postMessage
  console.log("UI Ready - Sending message to plugin");
  parent.postMessage({ pluginMessage: { type: 'UI_READY' } }, '*');
}); 