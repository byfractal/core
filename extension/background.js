// Background script pour l'extension HCentric UI Optimizer

console.log('HCentric UI Optimizer background script initialized');

// Écouteur pour gérer les messages du content script et du popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Message received in background:", message);
  
  if (message.type === "GET_INSIGHTS") {
    console.log("Request to get insights data from backend");
    fetchInsights()
      .then(data => {
        console.log("Insights data fetched successfully");
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error("Error fetching insights:", error);
        sendResponse({ success: false, error: error.message });
      });
    
    // Retourner true indique que sendResponse sera appelé de manière asynchrone
    return true;
  }
});

// Fonction pour récupérer les insights depuis le backend
async function fetchInsights() {
  try {
    console.log("Fetching insights from backend");
    const response = await fetch('http://localhost:8000/api/insights', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API responded with status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error in fetchInsights:", error);
    
    // En cas d'échec, essayer de charger le fichier de secours
    try {
      console.log("Attempting to load fallback file");
      const fallbackUrl = chrome.runtime.getURL('output/recommendation_output.json');
      const response = await fetch(fallbackUrl);
      
      if (!response.ok) {
        throw new Error(`Fallback file fetch failed with status: ${response.status}`);
      }
      
      return await response.json();
    } catch (fallbackError) {
      console.error("Fallback also failed:", fallbackError);
      throw new Error(`Failed to fetch insights: ${error.message}. Fallback also failed: ${fallbackError.message}`);
    }
  }
}

// Configurer les règles CORS pour permettre les requêtes vers le backend
chrome.declarativeNetRequest.updateDynamicRules({
  removeRuleIds: [1], // supprimer la règle existante si elle existe
  addRules: [{
    id: 1,
    priority: 1,
    action: {
      type: 'modifyHeaders',
      responseHeaders: [{
        header: 'Access-Control-Allow-Origin',
        operation: 'set',
        value: '*'
      }]
    },
    condition: {
      urlFilter: 'http://localhost:8000/*',
      resourceTypes: ['xmlhttprequest']
    }
  }]
}); 