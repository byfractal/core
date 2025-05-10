/**
 * Popup script for HCentric UI Optimizer Chrome Extension
 * Manages the UI interactions and communicates with the background service worker
 */

console.log('Popup script loading...');

import { ExtensionState, Insight } from './types';

// Expose to window for debugging
declare global {
  interface Window {
    hcentricUi: {
      showLoginView: () => void;
      showMainView: () => void;
      checkAuthState: () => void;
      debug: {
        getState: () => any;
      }
    }
  }
}

// DOM Elements
let loginView: HTMLDivElement | null = null;
let mainView: HTMLDivElement | null = null;
let insightsTab: HTMLDivElement | null = null;
let settingsTab: HTMLDivElement | null = null;
let apiKeyInput: HTMLInputElement | null = null;
let loginBtn: HTMLButtonElement | null = null;
let logoutBtn: HTMLButtonElement | null = null;
let refreshBtn: HTMLButtonElement | null = null;
let siteNameEl: HTMLHeadingElement | null = null;
let siteUrlEl: HTMLParagraphElement | null = null;
let insightsCards: HTMLDivElement | null = null;
let noInsightsEl: HTMLDivElement | null = null;
let loadingEl: HTMLDivElement | null = null;
let authStatusEl: HTMLDivElement | null = null;
let tabBtns: NodeListOf<Element> | null = null;
let notificationsToggle: HTMLInputElement | null = null;
let highlightingToggle: HTMLInputElement | null = null;

// Function to safely get DOM elements
function initializeDomElements() {
  console.log('Initializing DOM elements...');
  try {
    loginView = document.getElementById('login-view') as HTMLDivElement;
    mainView = document.getElementById('main-view') as HTMLDivElement;
    insightsTab = document.getElementById('insights-tab') as HTMLDivElement;
    settingsTab = document.getElementById('settings-tab') as HTMLDivElement;
    apiKeyInput = document.getElementById('api-key') as HTMLInputElement;
    loginBtn = document.getElementById('login-btn') as HTMLButtonElement;
    logoutBtn = document.getElementById('logout-btn') as HTMLButtonElement;
    refreshBtn = document.getElementById('refresh-btn') as HTMLButtonElement;
    siteNameEl = document.getElementById('site-name') as HTMLHeadingElement;
    siteUrlEl = document.getElementById('site-url') as HTMLParagraphElement;
    insightsCards = document.getElementById('insights-cards') as HTMLDivElement;
    noInsightsEl = document.getElementById('no-insights') as HTMLDivElement;
    loadingEl = document.querySelector('.loading') as HTMLDivElement;
    authStatusEl = document.getElementById('auth-status') as HTMLDivElement;
    tabBtns = document.querySelectorAll('.tab-btn');
    notificationsToggle = document.getElementById('notifications-toggle') as HTMLInputElement;
    highlightingToggle = document.getElementById('highlighting-toggle') as HTMLInputElement;
    
    // Log which elements were not found
    if (!loginView) console.error('Element not found: login-view');
    if (!mainView) console.error('Element not found: main-view');
    if (!insightsTab) console.error('Element not found: insights-tab');
    if (!settingsTab) console.error('Element not found: settings-tab');
    if (!apiKeyInput) console.error('Element not found: api-key');
    if (!loginBtn) console.error('Element not found: login-btn');
    if (!logoutBtn) console.error('Element not found: logout-btn');
    if (!refreshBtn) console.error('Element not found: refresh-btn');
    if (!siteNameEl) console.error('Element not found: site-name');
    if (!siteUrlEl) console.error('Element not found: site-url');
    if (!insightsCards) console.error('Element not found: insights-cards');
    if (!noInsightsEl) console.error('Element not found: no-insights');
    if (!loadingEl) console.error('Element not found: .loading');
    if (!authStatusEl) console.error('Element not found: auth-status');
    if (!tabBtns || tabBtns.length === 0) console.error('Elements not found: .tab-btn');
    if (!notificationsToggle) console.error('Element not found: notifications-toggle');
    if (!highlightingToggle) console.error('Element not found: highlighting-toggle');
    
    console.log('DOM elements initialization complete');
    return true;
  } catch (error) {
    console.error('Error initializing DOM elements:', error);
    return false;
  }
}

// Local state
interface LocalState {
  isAuthenticated: boolean;
  currentSite?: {
    name: string;
    url: string;
  };
  insights: Insight[];
  settings: {
    showNotifications: boolean;
    highlightElements: boolean;
  };
}

let state: LocalState = {
  isAuthenticated: false,
  insights: [],
  settings: {
    showNotifications: true,
    highlightElements: true
  }
};

// Initialize
document.addEventListener('DOMContentLoaded', initialize);

async function initialize() {
  console.log('Initializing popup...');
  
  // Initialize DOM elements
  if (!initializeDomElements()) {
    console.error('Failed to initialize DOM elements, aborting initialization');
    return;
  }
  
  // Expose functions to window for debugging
  window.hcentricUi = {
    showLoginView,
    showMainView,
    checkAuthState,
    debug: {
      getState: () => state
    }
  };
  
  // Check authentication state
  await checkAuthState();
  
  // Setup event listeners
  setupEventListeners();
  
  // Initialize settings
  loadSettings();
  
  // Get current tab info
  getCurrentTabInfo();
  
  console.log('Popup initialization complete');
  
  // Force login view by default for testing
  showLoginView();
}

// Check if user is authenticated
async function checkAuthState() {
  console.log('Checking authentication state...');
  chrome.storage.local.get(['hcentric_state'], (result) => {
    if (result.hcentric_state) {
      const savedState = JSON.parse(result.hcentric_state);
      console.log('Saved state:', savedState);
      if (savedState.isAuthenticated) {
        state.isAuthenticated = true;
        showMainView();
        
        // Fetch insights for current site if available
        if (savedState.activeSite) {
          chrome.runtime.sendMessage(
            { action: 'get_insights' },
            (response) => {
              console.log('Get insights response:', response);
              if (response && response.success && response.insights.length > 0) {
                state.insights = response.insights;
                renderInsights();
              }
            }
          );
        }
      } else {
        showLoginView();
      }
    } else {
      showLoginView();
    }
  });
}

// Setup event listeners
function setupEventListeners() {
  console.log('Setting up event listeners...');
  try {
    // Login button
    if (loginBtn) {
      loginBtn.addEventListener('click', handleLogin);
    }
    
    // Logout button
    if (logoutBtn) {
      logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Refresh button
    if (refreshBtn) {
      refreshBtn.addEventListener('click', handleRefreshInsights);
    }
    
    // Tab buttons
    if (tabBtns) {
      tabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
          const target = e.currentTarget as HTMLButtonElement;
          const tabName = target.getAttribute('data-tab');
          if (tabName) {
            switchTab(tabName);
          }
        });
      });
    }
    
    // Settings toggles
    if (notificationsToggle) {
      notificationsToggle.addEventListener('change', updateSettings);
    }
    
    if (highlightingToggle) {
      highlightingToggle.addEventListener('change', updateSettings);
    }
    
    console.log('Event listeners set up successfully');
  } catch (error) {
    console.error('Error setting up event listeners:', error);
  }
}

// Tab switching
function switchTab(tabName: string) {
  // Update tab buttons
  if (tabBtns) {
    tabBtns.forEach(btn => {
      const btnTabName = btn.getAttribute('data-tab');
      if (btnTabName === tabName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }
  
  // Update tab content
  if (tabName === 'insights' && insightsTab && settingsTab) {
    insightsTab.classList.remove('hidden');
    settingsTab.classList.add('hidden');
  } else if (tabName === 'settings' && insightsTab && settingsTab) {
    insightsTab.classList.add('hidden');
    settingsTab.classList.remove('hidden');
  }
}

// Load settings from storage
function loadSettings() {
  chrome.storage.local.get(['hcentric_settings'], (result) => {
    if (result.hcentric_settings) {
      state.settings = JSON.parse(result.hcentric_settings);
      if (notificationsToggle) {
        notificationsToggle.checked = state.settings.showNotifications;
      }
      if (highlightingToggle) {
        highlightingToggle.checked = state.settings.highlightElements;
      }
    }
  });
}

// Update settings
function updateSettings() {
  if (notificationsToggle && highlightingToggle) {
    state.settings = {
      showNotifications: notificationsToggle.checked,
      highlightElements: highlightingToggle.checked
    };
    
    chrome.storage.local.set({ 'hcentric_settings': JSON.stringify(state.settings) });
  }
}

// Handle login
function handleLogin() {
  if (!apiKeyInput) return;
  
  const apiKey = apiKeyInput.value.trim();
  
  if (!apiKey) {
    showError('Please enter your API key');
    return;
  }
  
  showLoading(true);
  chrome.runtime.sendMessage(
    { action: 'authenticate', apiKey },
    (response) => {
      showLoading(false);
      
      if (response && response.success) {
        state.isAuthenticated = true;
        showMainView();
        getCurrentTabInfo();
      } else {
        showError(response?.message || 'Authentication failed');
      }
    }
  );
}

// Handle logout
function handleLogout() {
  chrome.runtime.sendMessage(
    { action: 'log_out' },
    (response) => {
      if (response && response.success) {
        state.isAuthenticated = false;
        showLoginView();
      }
    }
  );
}

// Get current tab information
function getCurrentTabInfo() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length > 0 && tabs[0].url) {
      const currentTab = tabs[0];
      const url = new URL(currentTab.url || '');
      
      state.currentSite = {
        name: currentTab.title || url.hostname,
        url: url.toString()
      };
      
      if (siteNameEl) {
        siteNameEl.textContent = state.currentSite.name;
      }
      
      if (siteUrlEl) {
        siteUrlEl.textContent = url.hostname;
      }
      
      // If authenticated, fetch insights for this site
      if (state.isAuthenticated) {
        fetchInsights(url.toString());
      }
    }
  });
}

// Fetch insights for current site
function fetchInsights(siteUrl: string) {
  showLoading(true);
  
  chrome.runtime.sendMessage(
    { action: 'fetch_insights', siteUrl },
    (response) => {
      showLoading(false);
      
      if (response && response.success) {
        state.insights = response.insights;
        renderInsights();
      } else {
        showError(response?.message || 'Failed to fetch insights');
      }
    }
  );
}

// Handle refresh insights button
function handleRefreshInsights() {
  if (state.currentSite) {
    fetchInsights(state.currentSite.url);
  }
}

// Render insights
function renderInsights() {
  if (!insightsCards || !noInsightsEl) return;
  
  insightsCards.innerHTML = '';
  
  if (state.insights.length === 0) {
    noInsightsEl.classList.remove('hidden');
    return;
  }
  
  noInsightsEl.classList.add('hidden');
  
  // Get card template
  const template = document.getElementById('insight-card-template') as HTMLTemplateElement;
  if (!template) {
    console.error('Template not found: insight-card-template');
    return;
  }
  
  // Create a card for each insight
  state.insights.forEach(insight => {
    const card = template.content.cloneNode(true) as DocumentFragment;
    
    // Set card content
    const titleEl = card.querySelector('.insight-title') as HTMLHeadingElement;
    const descriptionEl = card.querySelector('.insight-description') as HTMLParagraphElement;
    const severityEl = card.querySelector('.severity') as HTMLDivElement;
    const highlightBtn = card.querySelector('.highlight-btn') as HTMLButtonElement;
    const applyBtn = card.querySelector('.apply-btn') as HTMLButtonElement;
    
    if (titleEl) titleEl.textContent = insight.title;
    if (descriptionEl) descriptionEl.textContent = insight.description;
    if (severityEl) severityEl.classList.add(`severity-${insight.severity}`);
    
    // Add data attribute for identification
    const cardEl = card.querySelector('.insight-card') as HTMLDivElement;
    if (cardEl) cardEl.setAttribute('data-insight-id', insight.id);
    
    // Setup buttons
    if (highlightBtn) {
      if (insight.selector && state.settings.highlightElements) {
        highlightBtn.addEventListener('click', () => highlightElement(insight.selector as string));
      } else {
        highlightBtn.disabled = true;
      }
    }
    
    if (applyBtn) {
      if (insight.fixAvailable) {
        applyBtn.addEventListener('click', () => applyFix(insight.id));
      } else {
        applyBtn.disabled = true;
      }
    }
    
    // Safely append to insights cards
    if (insightsCards) {
      insightsCards.appendChild(card);
    }
  });
}

// Highlight element on page
function highlightElement(selector: string) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length > 0 && tabs[0].id) {
      chrome.tabs.sendMessage(
        tabs[0].id,
        { action: 'highlight_element', selector }
      );
    }
  });
}

// Apply insight fix
function applyFix(insightId: string) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length > 0 && tabs[0].id) {
      const tabId = tabs[0].id;
      showLoading(true);
      
      chrome.runtime.sendMessage(
        { action: 'apply_fix', insightId, tabId },
        (response) => {
          showLoading(false);
          
          if (response && response.success) {
            showSuccess('Fix applied successfully');
            
            // Mark as applied in UI
            if (insightsCards) {
              const card = insightsCards.querySelector(`[data-insight-id="${insightId}"]`) as HTMLDivElement;
              if (card) {
                card.classList.add('applied');
                const applyBtn = card.querySelector('.apply-btn') as HTMLButtonElement;
                if (applyBtn) {
                  applyBtn.textContent = 'Applied';
                  applyBtn.disabled = true;
                }
              }
            }
          } else {
            showError(response?.message || 'Failed to apply fix');
          }
        }
      );
    }
  });
}

// View switching
function showLoginView() {
  console.log('Showing login view');
  if (loginView) loginView.classList.remove('hidden');
  if (mainView) mainView.classList.add('hidden');
  if (authStatusEl) {
    authStatusEl.textContent = 'Not connected';
    authStatusEl.className = 'status-disconnected';
  }
}

function showMainView() {
  console.log('Showing main view');
  if (loginView) loginView.classList.add('hidden');
  if (mainView) mainView.classList.remove('hidden');
  if (authStatusEl) {
    authStatusEl.textContent = 'Connected';
    authStatusEl.className = 'status-connected';
  }
}

// UI Helpers
function showLoading(show: boolean) {
  if (loadingEl) {
    if (show) {
      loadingEl.classList.remove('hidden');
    } else {
      loadingEl.classList.add('hidden');
    }
  }
}

function showError(message: string) {
  console.error('Error:', message);
  const errorEl = document.createElement('div');
  errorEl.className = 'error-message';
  errorEl.textContent = message;
  
  // Remove existing error messages
  document.querySelectorAll('.error-message').forEach(el => el.remove());
  
  document.body.appendChild(errorEl);
  
  // Auto remove after 3 seconds
  setTimeout(() => {
    errorEl.classList.add('fade-out');
    setTimeout(() => errorEl.remove(), 300);
  }, 3000);
}

function showSuccess(message: string) {
  console.log('Success:', message);
  const successEl = document.createElement('div');
  successEl.className = 'success-message';
  successEl.textContent = message;
  
  // Remove existing success messages
  document.querySelectorAll('.success-message').forEach(el => el.remove());
  
  document.body.appendChild(successEl);
  
  // Auto remove after 3 seconds
  setTimeout(() => {
    successEl.classList.add('fade-out');
    setTimeout(() => successEl.remove(), 300);
  }, 3000);
} 