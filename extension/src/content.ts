/**
 * Content script for HCentric UI Optimizer
 * This script is injected into target web pages to:
 * 1. Collect UI element data for analysis
 * 2. Apply UI optimizations based on insights
 * 3. Provide real-time feedback
 */

import { Insight } from './types';

// Track applied insights to avoid duplicates
const appliedInsights = new Set<string>();

// Show notification
function showNotification(message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = 'ext-hcentric-notification';
  notification.innerHTML = `
    <div class="ext-hcentric-notification-${type}">
      <div class="ext-hcentric-notification-content">${message}</div>
    </div>
  `;
  
  // Add to DOM
  document.body.appendChild(notification);
  
  // Remove after duration
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => notification.remove(), 300);
  }, duration);
}

// Apply UI changes based on insight
function applyInsightFix(insight: Insight): boolean {
  try {
    if (appliedInsights.has(insight.id)) {
      console.log(`Fix for insight ${insight.id} already applied`);
      return true;
    }
    
    if (!insight.selector) {
      console.error('No selector provided for insight fix');
      return false;
    }
    
    // Find target element
    const element = document.querySelector(insight.selector);
    if (!element) {
      console.error(`Element not found for selector: ${insight.selector}`);
      return false;
    }
    
    // Apply CSS modifications
    if (insight.cssModifications) {
      Object.entries(insight.cssModifications).forEach(([prop, value]) => {
        (element as HTMLElement).style.setProperty(prop, value);
      });
    }
    
    // Apply attribute changes
    if (insight.attributeChanges) {
      Object.entries(insight.attributeChanges).forEach(([attr, value]) => {
        element.setAttribute(attr, value);
      });
    }
    
    // Apply innerHTML if provided
    if (insight.innerHTML !== undefined) {
      element.innerHTML = insight.innerHTML;
    }
    
    // Mark as applied
    appliedInsights.add(insight.id);
    
    showNotification(`Optimization applied: ${insight.title}`, 'success');
    return true;
  } catch (error) {
    console.error('Failed to apply insight fix:', error);
    return false;
  }
}

// Collect page structure for analysis
function collectPageData(): Record<string, any> {
  const pageData: Record<string, any> = {
    url: window.location.href,
    title: document.title,
    meta: {} as Record<string, string>,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight
    },
    elements: []
  };
  
  // Collect meta tags
  document.querySelectorAll('meta').forEach(meta => {
    const name = meta.getAttribute('name') || meta.getAttribute('property');
    const content = meta.getAttribute('content');
    if (name && content) {
      pageData.meta[name] = content;
    }
  });
  
  // Collect important elements (CTAs, forms, navigation)
  const importantElements = [
    ...Array.from(document.querySelectorAll('button, a.btn, a.button, [role="button"]')),
    ...Array.from(document.querySelectorAll('form')),
    ...Array.from(document.querySelectorAll('nav, [role="navigation"]')),
    ...Array.from(document.querySelectorAll('header, footer, main, [role="main"]'))
  ];
  
  // Extract relevant info for each element
  importantElements.forEach(element => {
    // Generate a selector for this element
    const selector = getCssSelector(element);
    
    // Get basic info
    const rect = element.getBoundingClientRect();
    const styles = window.getComputedStyle(element);
    
    pageData.elements.push({
      type: element.tagName.toLowerCase(),
      id: element.id,
      classes: Array.from(element.classList),
      text: element.textContent?.trim().substring(0, 100),
      selector: selector,
      visible: isElementVisible(element),
      position: {
        x: rect.left,
        y: rect.top,
        width: rect.width,
        height: rect.height
      },
      styles: {
        backgroundColor: styles.backgroundColor,
        color: styles.color,
        fontSize: styles.fontSize,
        fontWeight: styles.fontWeight
      }
    });
  });
  
  return pageData;
}

// Generate a unique CSS selector for an element
function getCssSelector(element: Element): string {
  if (element.id) {
    return `#${element.id}`;
  }
  
  if (element.classList.length > 0) {
    return `${element.tagName.toLowerCase()}.${Array.from(element.classList).join('.')}`;
  }
  
  // Fallback to a more complex selector
  const path = [];
  let current = element;
  
  while (current && current !== document.body) {
    let selector = current.tagName.toLowerCase();
    
    if (current.id) {
      selector += `#${current.id}`;
      path.unshift(selector);
      break;
    } else {
      const sibling = current.parentElement?.children;
      if (sibling && sibling.length > 1) {
        const index = Array.from(sibling).indexOf(current) + 1;
        selector += `:nth-child(${index})`;
      }
      
      path.unshift(selector);
      current = current.parentElement as Element;
    }
  }
  
  return path.join(' > ');
}

// Check if an element is visible
function isElementVisible(element: Element): boolean {
  const styles = window.getComputedStyle(element);
  return styles.display !== 'none' && 
         styles.visibility !== 'hidden' && 
         styles.opacity !== '0';
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'collect_page_data':
      const pageData = collectPageData();
      sendResponse({ success: true, data: pageData });
      break;
    
    case 'apply_fix':
      const success = applyInsightFix(request.insight);
      sendResponse({ success });
      break;
    
    case 'highlight_element':
      highlightElement(request.selector);
      sendResponse({ success: true });
      break;
      
    default:
      sendResponse({ success: false, message: 'Unknown action' });
  }
  return true; // Keep the message channel open for async response
});

// Highlight an element
function highlightElement(selector: string) {
  const element = document.querySelector(selector);
  if (!element) return;
  
  // Store original styles
  const originalOutline = (element as HTMLElement).style.outline;
  const originalBoxShadow = (element as HTMLElement).style.boxShadow;
  
  // Apply highlight
  (element as HTMLElement).style.outline = '3px solid #2196F3';
  (element as HTMLElement).style.boxShadow = '0 0 10px rgba(33, 150, 243, 0.5)';
  
  // Remove highlight after 3 seconds
  setTimeout(() => {
    (element as HTMLElement).style.outline = originalOutline;
    (element as HTMLElement).style.boxShadow = originalBoxShadow;
  }, 3000);
}

// Announce to the background script that the content script has loaded
chrome.runtime.sendMessage({ action: 'content_loaded', url: window.location.href });

// CSS Styles
const styleSheet = document.createElement('style');
styleSheet.innerHTML = `
  .ext-hcentric-notification {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    font-size: 14px;
    line-height: 1.5;
    transition: all 0.3s ease;
  }
  
  .ext-hcentric-highlight {
    position: relative;
    z-index: 9998;
  }
  
  .ext-hcentric-highlight::after {
    content: '';
    position: absolute;
    top: -3px;
    left: -3px;
    right: -3px;
    bottom: -3px;
    background: transparent;
    border: 3px solid #2196F3;
    z-index: 9997;
    border-radius: 3px;
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(33, 150, 243, 0); }
    100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
  }
`;
document.head.appendChild(styleSheet); 