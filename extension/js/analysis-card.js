// Globally store the insights data
let insightsData = null;

// Initialization
document.addEventListener('DOMContentLoaded', function() {
  // Back button handler
  document.getElementById('back-button').addEventListener('click', function() {
    parent.postMessage({ type: 'NAVIGATE_BACK' }, '*');
  });
  
  // Reload button handler
  document.getElementById('reload-button').addEventListener('click', function() {
    fetchInsights();
  });
  
  // Initial load
  fetchInsights();
});

// Fetch insights from the backend with auto-retry
async function fetchInsights(retryCount = 0) {
  const loadingIndicator = document.getElementById('loading-indicator');
  const errorMessage = document.getElementById('error-message');
  const cardsContainer = document.getElementById('analysis-cards-container');
  
  // Show loading indicator
  loadingIndicator.style.display = 'block';
  loadingIndicator.textContent = retryCount > 0 ? `Loading insights... (attempt ${retryCount+1})` : 'Loading insights...';
  errorMessage.style.display = 'none';
  cardsContainer.innerHTML = '';
  
  try {
    // Try API endpoint first with a short timeout
    let data = null;
    const timeoutDuration = 3000; // 3 seconds timeout
    
    try {
      // Use Promise.race to implement timeout
      const fetchPromise = fetch('http://localhost:8000/api/insights');
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('API request timed out')), timeoutDuration)
      );
      
      const response = await Promise.race([fetchPromise, timeoutPromise]);
      if (response.ok) {
        data = await response.json();
      } else {
        throw new Error('API request failed with status ' + response.status);
      }
    } catch (apiError) {
      console.log('API endpoint failed, using fallback:', apiError);
      
      // Automatically fall back to local file
      try {
        const fallbackUrl = chrome.runtime.getURL('output/recommendation_output.json');
        const response = await fetch(fallbackUrl);
        if (response.ok) {
          data = await response.json();
          console.log("Loaded fallback data:", data);
        } else {
          throw new Error('Fallback request failed');
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        
        // If we have retry attempts left, retry after a delay
        if (retryCount < 2) {
          setTimeout(() => fetchInsights(retryCount + 1), 1000);
          return;
        }
        
        throw new Error('Both API and fallback failed');
      }
    }
    
    // Store data globally
    insightsData = data;
    
    // Update page title - try to use a relevant page name from the data
    if (data.page_id) {
      document.getElementById('page-title').textContent = data.page_id;
    } else if (data.insights && data.insights.length > 0 && data.insights[0].issueTitle) {
      // Extract page URL from the first insight title if possible
      const titleParts = data.insights[0].issueTitle.split(' ');
      const pageUrl = titleParts.find(part => part.startsWith('https://'));
      document.getElementById('page-title').textContent = pageUrl || 'App Analysis';
    } else {
      document.getElementById('page-title').textContent = 'App Analysis';
    }
    
    // Render cards
    renderInsightCards(data);
    
    // Hide loading indicator
    loadingIndicator.style.display = 'none';
    
  } catch (error) {
    console.error('Error fetching insights:', error);
    loadingIndicator.style.display = 'none';
    errorMessage.style.display = 'block';
    errorMessage.textContent = 'Failed to load insights: ' + error.message + '. Click Reload Data to try again.';
  }
}

// Render insight cards from JSON data
function renderInsightCards(data) {
  const cardsContainer = document.getElementById('analysis-cards-container');
  cardsContainer.innerHTML = '';
  
  // Handle different JSON structures (recommendations or insights)
  const items = data.recommendations || data.insights || [];
  
  if (items.length === 0) {
    cardsContainer.innerHTML = '<p>No insights available.</p>';
    return;
  }
  
  console.log("Rendering items:", items);
  
  // For each item in the data
  items.forEach((item, index) => {
    // Create card element
    const card = document.createElement('div');
    card.className = 'analysis-card';
    card.dataset.index = index;
    
    // Map fields based on the data structure
    const title = item.title || item.issueTitle || 'Unnamed issue';
    const priority = item.priority || (item.severity === 'needs-improvement' ? 'medium' : 'high');
    const description = item.description || (item.rootCause ? item.rootCause.context : '');
    const justification = item.justification || (item.rootCause ? item.rootCause.contextualData : '');
    const metricText = item.rootCause && item.rootCause.metric ? item.rootCause.metric.text : '';
    const impact = item.rootCause && item.rootCause.conversionImpact ? item.rootCause.conversionImpact : '';
    const fix = item.recommendedFix ? item.recommendedFix.suggestion : (item.before_after ? item.before_after.after : '');
    const component = item.component || (item.rootCause ? item.rootCause.source : '');
    const location = item.location || (item.recommendedFix ? item.recommendedFix.source : '');
    const expectedImpact = item.expected_impact || item.impactEstimate || '';
    const tags = item.tags || [];
    
    // Determine severity class
    let severityClass = 'minor';
    if (priority === 'high' || item.severity === 'high') {
      severityClass = 'underperforming';
    } else if (priority === 'medium' || item.severity === 'needs-improvement') {
      severityClass = 'needs-improvement';
    }
    
    // Format the recommendation data into HTML
    card.innerHTML = `
      <!-- Issue Header & Severity -->
      <div class="analysis-card-header">
        <div class="issue-title">${title}</div>
        <div class="severity-tag ${severityClass}">
          <span>${severityClass === 'underperforming' ? 'Underperforming' : 
                severityClass === 'needs-improvement' ? 'Needs improvement' : 'Minor issue'}</span>
        </div>
      </div>
      
      <!-- Separator -->
      <div class="separator"></div>
      
      <!-- Root Cause Section -->
      <div class="analysis-section">
        <div class="section-title">📊 Root cause</div>
        <div class="section-content">
          <div class="section-content-context">${description}</div>
          
          ${metricText ? `
          <!-- Supporting Metric -->
          <div class="supporting-metric">
            <span>${metricText}</span>
          </div>
          ` : ''}
          
          ${justification ? `
          <!-- Contextual Data -->
          <p class="contextual-data">${justification}</p>
          ` : ''}
          
          ${impact ? `
          <!-- Conversion Impact Warning -->
          <p class="conversion-impact">⚠️ ${impact}
            ${item.rootCause && item.rootCause.source ? `
            <!-- Source Badge -->
            <span class="source-badge">
              <span>${item.rootCause.source}</span>
              <span class="link-icon">
                <svg width="9" height="10" viewBox="0 0 9 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4.80833 7.26284L4.24264 7.82852C3.86757 8.20359 3.35886 8.41431 2.82843 8.41431C2.29799 8.41431 1.78929 8.20359 1.41421 7.82852C1.03914 7.45345 0.828427 6.94474 0.828427 6.41431C0.828427 5.88387 1.03914 5.37517 1.41421 5.00009L1.9799 4.43441" stroke="#64748B" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M3.677 2.7373L4.24269 2.17162C4.61776 1.79655 5.12647 1.58583 5.6569 1.58583C6.18733 1.58583 6.69604 1.79655 7.07111 2.17162C7.44619 2.54669 7.6569 3.0554 7.6569 3.58583C7.6569 4.11627 7.44619 4.62497 7.07111 5.00005L6.50543 5.56573" stroke="#64748B" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M3.11133 6.13159L5.37407 3.86885" stroke="#64748B" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </span>
            ` : ''}
          </p>
          ` : ''}
        </div>
      </div>
      
      <!-- Recommended Fix Section -->
      <div class="analysis-section">
        <div class="section-title">🔧 Recommended fix</div>
        <div class="section-content">
          <p class="actionable-suggestion">${fix || 'No specific recommendation available.'}
            <!-- Source Badge -->
            <span class="source-badge">
              <span>${location || component || 'Component'}</span>
              <span class="link-icon">
                <svg width="9" height="10" viewBox="0 0 9 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4.80833 7.26284L4.24264 7.82852C3.86757 8.20359 3.35886 8.41431 2.82843 8.41431C2.29799 8.41431 1.78929 8.20359 1.41421 7.82852C1.03914 7.45345 0.828427 6.94474 0.828427 6.41431C0.828427 5.88387 1.03914 5.37517 1.41421 5.00009L1.9799 4.43441" stroke="#64748B" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M3.677 2.7373L4.24269 2.17162C4.61776 1.79655 5.12647 1.58583 5.6569 1.58583C6.18733 1.58583 6.69604 1.79655 7.07111 2.17162C7.44619 2.54669 7.6569 3.0554 7.6569 3.58583C7.6569 4.11627 7.44619 4.62497 7.07111 5.00005L6.50543 5.56573" stroke="#64748B" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M3.11133 6.13159L5.37407 3.86885" stroke="#64748B" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </span>
          </p>
        </div>
      </div>
      
      <!-- Impact Estimate Section -->
      <div class="analysis-section">
        <div class="section-title">📈 Impact estimate</div>
        <div class="section-content">
          <p class="impact-estimate">${expectedImpact || 'No impact estimate available.'}</p>
        </div>
      </div>
      
      <!-- Separator -->
      <div class="separator"></div>
      
      <!-- Footer with Sources & Tags -->
      <div class="analysis-card-footer">
        <div class="source-composite">
          <div class="source-label">
            <div class="avatar-group">
              <div class="avatar avatar-1"></div>
              <div class="avatar avatar-2"></div>
            </div>
            <span>Source</span>
          </div>
        </div>
        
        <div class="insight-tags">
          ${tags.length > 0 ? 
            tags.map(tag => `
              <div class="insight-tag">
                <span>${tag}</span>
              </div>
            `).join('') :
            `
            <div class="insight-tag">
              <span>${component || 'Layout'}</span>
            </div>
            `
          }
        </div>
      </div>
      
      <!-- Fix Issue Button -->
      <button class="fix-issue-button ${!item.dom_patch || !item.dom_patch.selector ? 'disabled' : ''}" 
              id="fix-issue-button-${index}" 
              ${!item.dom_patch || !item.dom_patch.selector ? 'disabled' : ''}>
        Fix Issue
      </button>
    `;
    
    // Add the card to the container
    cardsContainer.appendChild(card);
    
    // Add event listener for the Fix Issue button (only if not disabled)
    if (item.dom_patch && item.dom_patch.selector) {
      card.querySelector(`#fix-issue-button-${index}`).addEventListener('click', function() {
        fixIssue(index, item);
      });
    }
  });
}

// Function to handle fixing an issue
function fixIssue(index, item) {
  console.log(`Fixing issue ${index}:`, item);
  
  // Send message to parent (main plugin code)
  parent.postMessage({ 
    type: 'FIX_ISSUE', 
    issueId: item.id || `issue-${index}`,
    item: item
  }, '*');
}

// Event listener for messages from the parent frame
window.addEventListener('message', function(event) {
  // Handle message events from parent
  if (event.data && event.data.type === 'REFRESH_DATA') {
    fetchInsights();
  }
}); 