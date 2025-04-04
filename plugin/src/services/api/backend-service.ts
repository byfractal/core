/**
 * Service pour la communication avec le backend
 */
export class BackendService {
  // URL de base de l'API backend
  private static baseUrl = "https://api.example.com";

  /**
   * Envoie les données d'interface extraites au backend
   * @param data Les données à envoyer
   * @returns Une promesse avec la réponse
   */
  public static async sendExtractedInterface(data: any): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/interfaces`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error sending data to backend:", error);
      throw error;
    }
  }

  /**
   * Obtient les données d'interface depuis le backend
   * @param id L'identifiant de l'interface
   * @returns Une promesse avec les données
   */
  public static async getInterface(id: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/interfaces/${id}`);

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching interface from backend:", error);
      throw error;
    }
  }
}
