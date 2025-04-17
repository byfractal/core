/**
 * Service pour gérer l'API Clerk et l'authentification
 * Ce service fournit des méthodes pour interagir avec Clerk API
 */

// Type pour la session Clerk
interface ClerkSession {
  token: string;
  user: {
    id: string;
    [key: string]: any;
  };
}

// Méthode pour stocker un token dans le localStorage Figma (synchronisé)
const storeClerkToken = (token: string): boolean => {
  try {
    localStorage.setItem("clerk_token", token);
    console.log("Token stocké avec succès");
    return true;
  } catch (error) {
    console.error("Erreur lors du stockage du token:", error);
    return false;
  }
};

// Méthode pour récupérer un token du localStorage
const getStoredClerkToken = (): string | null => {
  try {
    return localStorage.getItem("clerk_token");
  } catch (error) {
    console.error("Erreur lors de la récupération du token:", error);
    return null;
  }
};

// Envoyer les informations d'authentification à Figma
const sendAuthToFigma = (session: ClerkSession): void => {
  try {
    // Envoyer un message à Figma indiquant le succès de l'authentification
    parent.postMessage(
      {
        pluginMessage: {
          type: "CLERK_AUTH_SUCCESS",
          userId: session.user.id,
          userInfo: session.user,
        },
      },
      "*"
    );

    // Stocker également le token
    storeClerkToken(session.token);
  } catch (error) {
    console.error("Erreur lors de l'envoi des informations à Figma:", error);
  }
};

// Valider un token (simulation)
const validateToken = async (token: string): Promise<boolean> => {
  try {
    console.log("Validation du token:", token.substring(0, 10) + "...");

    // Simulation d'une validation (à remplacer par un vrai appel API)
    // Dans un environnement de production, appelez l'API Clerk pour valider
    return token.length > 20;
  } catch (error) {
    console.error("Erreur lors de la validation du token:", error);
    return false;
  }
};

// Appel à l'API Clerk (simulation)
const callClerkAPI = async (
  endpoint: string,
  method: string = "GET",
  data?: any
): Promise<any> => {
  try {
    console.log(`Appel API Clerk: ${method} ${endpoint}`);

    // Simulation d'un appel réussi (à remplacer par un vrai appel API)
    return {
      success: true,
      message: `Appel simulé à ${endpoint} avec méthode ${method}`,
      data: data || {},
    };
  } catch (error) {
    console.error(`Erreur lors de l'appel à l'API Clerk (${endpoint}):`, error);
    throw error;
  }
};

// Exporter les méthodes
export default {
  storeClerkToken,
  getStoredClerkToken,
  sendAuthToFigma,
  validateToken,
  callClerkAPI,
};
