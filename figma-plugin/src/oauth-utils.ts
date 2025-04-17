/**
 * Utilitaires pour le flux OAuth PKCE (Proof Key for Code Exchange)
 * Ces fonctions génèrent et manipulent les valeurs nécessaires pour PKCE
 */

/**
 * Génère un code_verifier aléatoire pour PKCE
 * @returns Une chaîne aléatoire de 43-128 caractères
 */
export function generateCodeVerifier(): string {
  // Génère une chaîne aléatoire utilisant uniquement des caractères sûrs pour URL
  const array = new Uint8Array(56);
  crypto.getRandomValues(array);

  return base64UrlEncode(array);
}

/**
 * Génère un code_challenge à partir du code_verifier en utilisant SHA-256
 * @param codeVerifier Le code_verifier à transformer
 * @returns Le code_challenge
 */
export async function generateCodeChallenge(
  codeVerifier: string
): Promise<string> {
  // Encoder la chaîne en UTF-8
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);

  // Calculer le hash SHA-256
  const hash = await crypto.subtle.digest("SHA-256", data);

  // Convertir le hash en une chaîne base64url
  return base64UrlEncode(new Uint8Array(hash));
}

/**
 * Encode un tableau d'octets en base64url
 * @param buffer Tableau d'octets à encoder
 * @returns Chaîne encodée en base64url
 */
function base64UrlEncode(buffer: Uint8Array): string {
  // Convertir le buffer en chaîne base64
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));

  // Convertir la chaîne base64 en base64url
  return base64
    .replace(/\+/g, "-") // Remplacer + par -
    .replace(/\//g, "_") // Remplacer / par _
    .replace(/=+$/, ""); // Supprimer les = de padding
}

/**
 * Fonction utilitaire pour analyser les paramètres d'URL
 * Utilisée pour extraire le code d'autorisation de l'URL de callback
 * @param url L'URL à analyser
 * @returns Un objet contenant les paramètres d'URL
 */
export function parseUrlParams(url: string): Record<string, string> {
  const params: Record<string, string> = {};
  const queryString = url.split("?")[1];

  if (!queryString) {
    return params;
  }

  const pairs = queryString.split("&");

  for (const pair of pairs) {
    const [key, value] = pair.split("=");
    params[decodeURIComponent(key)] = decodeURIComponent(value || "");
  }

  return params;
}

/**
 * Vérifie que l'état retourné correspond à l'état envoyé
 * Protection contre les attaques CSRF
 * @param sentState L'état envoyé
 * @param receivedState L'état reçu
 * @returns true si les états correspondent, false sinon
 */
export function validateState(
  sentState: string,
  receivedState: string
): boolean {
  return sentState === receivedState;
}
