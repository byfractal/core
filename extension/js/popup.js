// Montrer/cacher panel debug avec Alt+D ou Shift+D
document.addEventListener('DOMContentLoaded', function() {
  // Debug panel toggle
  document.addEventListener('keydown', function(e) {
    if ((e.altKey || e.shiftKey) && e.key === 'd') {
      document.getElementById('debug-panel').classList.toggle('show');
    }
  });
  
  // Navigation via boutons debug
  document.querySelectorAll('.debug-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const page = this.dataset.page;
      navigateToPage(page);
    });
  });
});

// Fonction pour changer de page
function navigateToPage(pageName) {
  const iframe = document.getElementById('content-frame');
  iframe.src = `pages/${pageName}.html`;
  document.getElementById('current-page').textContent = pageName;
}

// Écouteur de messages provenant de l'iframe
window.addEventListener('message', function(event) {
  // Vérifier si le message vient de notre iframe
  const iframe = document.getElementById('content-frame');
  if (iframe && event.source === iframe.contentWindow) {
    const message = event.data.pluginMessage;
    
    // Traiter les messages de navigation
    if (message && message.type) {
      console.log('Message reçu de l\'iframe:', message);
      
      switch (message.type) {
        case 'NAVIGATE_TO_PROJECTS':
          navigateToPage('ProjectsPage');
          break;
        case 'NAVIGATE_TO_PROJECT_OVERVIEW':
          navigateToPage('ProjectOverviewPage');
          break;
        case 'NEW_OPTIMIZATION':
        case 'IMPORT_DATA':
          navigateToPage('ImportPage');
          break;
        case 'VIEW_OPTIMIZATION':
          navigateToPage('AnalysisCardPage');
          break;
      }
    }
  }
});

// Communication avec le script de contenu Chrome
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Message reçu du background:', message);
  
  // Répondre si nécessaire
  sendResponse({ success: true });
  return true; // Garder la connexion ouverte pour les réponses asynchrones
}); 