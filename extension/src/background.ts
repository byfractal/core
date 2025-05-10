/**
 * Background service worker for HCentric UI Optimizer
 * Handles API communication and manages extension state
 */

import { ExtensionState, Insight } from './types';

// Global state
let state: ExtensionState = {
  isAuthenticated: false,
  insights: [],
  settings: {
    showNotifications: true,
    highlightElements: true
  }
};

// Initialize state from storage
chrome.storage.local.get(['hcentric_state'], (result) => {
  if (result.hcentric_state) {
    state = JSON.parse(result.hcentric_state);
    // Ensure settings exists (for backward compatibility)
    if (!state.settings) {
      state.settings = {
        showNotifications: true,
        highlightElements: true
      };
    }
  }
});

// Save state to storage
function saveState() {
  chrome.storage.local.set({ 'hcentric_state': JSON.stringify(state) });
}

// Message handlers
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'authenticate':
      handleAuthentication(request.apiKey, sendResponse);
      break;
    case 'fetch_insights':
      fetchInsightsFromAPI(request.siteUrl, sendResponse);
      break;
    case 'get_insights':
      sendResponse({ success: true, insights: state.insights });
      break;
    case 'apply_fix':
      applyFix(request.insightId, request.tabId, sendResponse);
      break;
    case 'log_out':
      logOut(sendResponse);
      break;
    default:
      sendResponse({ success: false, message: 'Unknown action' });
  }
  return true; // Keep the message channel open for async response
});

// Authentication handler
async function handleAuthentication(apiKey: string, sendResponse: (response: any) => void) {
  try {
    // Simple validation (in production, would verify against backend)
    if (!apiKey || apiKey.length < 8) {
      sendResponse({ success: false, message: 'Invalid API key format' });
      return;
    }
    
    // Store API key and update state
    state.apiKey = apiKey;
    state.isAuthenticated = true;
    saveState();
    
    sendResponse({ success: true });
  } catch (error) {
    console.error('Authentication error:', error);
    sendResponse({ success: false, message: 'Authentication failed' });
  }
}

// Fetch insights from API
async function fetchInsightsFromAPI(siteUrl: string, sendResponse: (response: any) => void) {
  try {
    if (!state.apiKey) {
      sendResponse({ success: false, message: 'Not authenticated' });
      return;
    }
    
    // In a real implementation, this would call your backend API
    // Mock implementation for now
    const mockInsights: Insight[] = [
      {
        id: 'insight1',
        title: 'High friction in checkout form',
        description: 'Users are spending more time than expected on the checkout form',
        severity: 'high',
        pageUrl: '/checkout',
        timestamp: new Date().toISOString(),
        fixAvailable: true
      },
      {
        id: 'insight2',
        title: 'Low CTR on hero section',
        description: 'The main call-to-action has below average click rates',
        severity: 'medium',
        pageUrl: '/',
        timestamp: new Date().toISOString(),
        fixAvailable: true
      }
    ];
    
    // Update state
    state.insights = mockInsights;
    state.activeSite = siteUrl;
    state.lastFetch = Date.now();
    saveState();
    
    sendResponse({ success: true, insights: mockInsights });
  } catch (error) {
    console.error('Failed to fetch insights:', error);
    sendResponse({ success: false, message: 'Failed to fetch insights' });
  }
}

// Apply insight fix
async function applyFix(insightId: string, tabId: number, sendResponse: (response: any) => void) {
  try {
    // Find the insight
    const insight = state.insights.find(i => i.id === insightId);
    if (!insight) {
      sendResponse({ success: false, message: 'Insight not found' });
      return;
    }
    
    // Send message to content script to apply the fix
    chrome.tabs.sendMessage(tabId, {
      action: 'apply_fix',
      insight: insight
    }, (response) => {
      if (response && response.success) {
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, message: response?.message || 'Failed to apply fix' });
      }
    });
  } catch (error) {
    console.error('Failed to apply fix:', error);
    sendResponse({ success: false, message: 'Failed to apply fix' });
  }
}

// Log out
function logOut(sendResponse: (response: any) => void) {
  // Reset state
  state = {
    isAuthenticated: false,
    insights: [],
    settings: {
      showNotifications: true,
      highlightElements: true
    }
  };
  saveState();
  
  sendResponse({ success: true });
}

// Listen for tab updates to inject content script if needed
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url?.startsWith('http')) {
    // Check if we have insights for this page
    if (state.insights && state.insights.length > 0) {
      const pageUrl = new URL(tab.url).pathname;
      const insightsForPage = state.insights.filter(i => i.pageUrl === pageUrl);
      
      if (insightsForPage.length > 0) {
        // Notify the popup that we have insights for this page
        chrome.runtime.sendMessage({
          action: 'page_has_insights',
          insights: insightsForPage
        });
      }
    }
  }
}); 