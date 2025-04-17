/**
 * Fonctions de test pour vérifier la connexion avec Clerk
 * Ce fichier permet de tester la configuration Clerk dans l'environnement Figma
 */

import clerkAPI from "./services/clerk-api";

/**
 * Teste la connexion avec Clerk et vérifie la configuration
 * @returns {Promise<boolean>} Succès ou échec du test
 */
export const testClerkConnection = async (): Promise<boolean> => {
  try {
    console.log("🧪 Début du test de connexion Clerk...");

    // Vérifier si la clé publishable est configurée
    const publishableKey =
      process.env.VITE_CLERK_PUBLISHABLE_KEY ||
      (window as any).__VITE_CLERK_PUBLISHABLE_KEY ||
      (window as any).VITE_CLERK_PUBLISHABLE_KEY;

    console.log("🔑 Clé trouvée?", !!publishableKey);

    if (!publishableKey) {
      console.error("❌ Erreur: Clé publishable Clerk manquante");
      return false;
    }

    // Vérifier le stockage local
    const testToken = "test_token_" + Date.now();
    const storageResult = clerkAPI.storeClerkToken(testToken);
    console.log("💾 Stockage local fonctionnel:", storageResult);

    if (!storageResult) {
      console.error("❌ Erreur: Problème de stockage local");
      return false;
    }

    // Vérifier la communication avec Figma
    try {
      parent.postMessage(
        {
          pluginMessage: {
            type: "TEST_CONNECTION",
            success: true,
          },
        },
        "*"
      );
      console.log("📤 Message envoyé à Figma");
    } catch (error) {
      console.error("❌ Erreur lors de l'envoi du message à Figma:", error);
      return false;
    }

    console.log("✅ Test de connexion Clerk réussi!");
    return true;
  } catch (error) {
    console.error("❌ Erreur lors du test de connexion Clerk:", error);
    return false;
  }
};
