import { ExtensionCommunicationService } from "./services/extension/communication";
import { DesignChangesCollectionInterface } from "./types/design-changes";
import { RecommendationApplierService } from "./services/design/recommendation-applier";

/**
 * Point d'entrée du plugin Figma
 */
figma.showUI(__html__, { width: 450, height: 600 });

// Initialisation du service de communication avec l'extension
ExtensionCommunicationService.initialize();

// État des recommandations
let currentRecommendations: DesignChangesCollectionInterface | null = null;

// Gestion des messages de l'interface utilisateur
figma.ui.onmessage = async (msg) => {
  switch (msg.type) {
    case "cancel":
      figma.closePlugin();
      break;

    case "import-html":
      // Notification à l'utilisateur
      figma.notify("Ready to receive HTML interface data");
      break;

    case "fetch-recommendations":
      // Ici, vous feriez un appel à votre backend pour obtenir les recommandations
      // Pour l'exemple, nous utilisons des données simulées
      currentRecommendations = await fetchMockRecommendations();
      figma.ui.postMessage({
        type: "recommendations-loaded",
        recommendations: currentRecommendations,
      });
      break;

    case "apply-recommendations":
      if (
        currentRecommendations &&
        msg.collectionId === currentRecommendations.id
      ) {
        figma.ui.postMessage({ type: "apply-started" });

        try {
          const results = await RecommendationApplierService.applyChanges(
            currentRecommendations
          );
          figma.ui.postMessage({
            type: "apply-completed",
            results,
          });

          figma.notify(
            `Applied ${results.success} of ${results.total} recommendations`
          );
        } catch (error) {
          console.error("Error applying recommendations:", error);
          figma.ui.postMessage({
            type: "apply-error",
            error: "Failed to apply recommendations",
          });

          figma.notify("Failed to apply recommendations", { error: true });
        }
      }
      break;

    default:
      break;
  }
};

// Fonction temporaire pour simuler des recommandations
async function fetchMockRecommendations(): Promise<DesignChangesCollectionInterface> {
  // Simulation d'un délai réseau
  await new Promise((resolve) => setTimeout(resolve, 500));

  return {
    id: "rec_" + Date.now(),
    title: "Login Form Optimization",
    description:
      "Recommendations to improve the login form UX based on user session analysis",
    changes: [
      {
        id: "change_1",
        action: "UPDATE",
        targetId: figma.currentPage.selection[0]?.id || "unknown",
        properties: {
          style: {
            fill: {
              color: { r: 0.25, g: 0.52, b: 0.96 },
            },
            cornerRadius: 8,
          },
          layout: {
            width: 280,
          },
        },
        metadata: {
          reasonForChange:
            "Increase button visibility to improve conversion rate",
          expectedImprovement: "14% increase in successful logins",
          confidenceScore: 0.85,
          dataPoints: ["heatmap_analysis", "session_recordings"],
        },
      },
      {
        id: "change_2",
        action: "CREATE",
        elementType: "TEXT",
        properties: {
          text: {
            content: "Forgot password?",
            fontSize: 14,
            fontFamily: "Inter",
            textAlign: "CENTER",
          },
          layout: {
            x: 150,
            y: 250,
          },
        },
        metadata: {
          reasonForChange:
            "Users often struggle to find password recovery option",
          expectedImprovement: "Reduce support tickets by 22%",
          confidenceScore: 0.78,
          dataPoints: ["support_ticket_analysis", "user_interviews"],
        },
      },
    ],
    metrics: {
      expectedImprovementScore: 78,
      impactAreas: ["User Experience", "Conversion Rate", "Support Efficiency"],
      priority: "HIGH",
      implementationComplexity: "LOW",
    },
    timestamp: Date.now(),
    version: "1.0.0",
  };
}

// Message initial
figma.ui.postMessage({ type: "plugin-loaded" });
