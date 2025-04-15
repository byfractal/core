/**
 * Sends a message to the Figma plugin
 * @param {Object} message - The message to send
 */
function sendMessageToPlugin(message) {
  parent.postMessage({ pluginMessage: message }, '*');
}

/**
 * Formats a date for display
 * @param {Date|string} date - The date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
  // If date is a string, try to convert it to a Date object
  if (typeof date === 'string') {
    // Check if it's a relative date string like "1 hour ago"
    if (date.includes(' ago') || date === 'Yesterday' || date.includes('Last')) {
      return date; // Return the relative date string as is
    }
    
    // Otherwise, try to parse it as a date
    date = new Date(date);
  }

  // Check if the date is today
  const today = new Date();
  if (date.setHours(0, 0, 0, 0) === today.setHours(0, 0, 0, 0)) {
    return 'Today';
  }

  // Check if the date is yesterday
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  if (date.setHours(0, 0, 0, 0) === yesterday.setHours(0, 0, 0, 0)) {
    return 'Yesterday';
  }

  // Check if the date is in the last week
  const lastWeek = new Date();
  lastWeek.setDate(lastWeek.getDate() - 7);
  if (date >= lastWeek) {
    return 'Last week';
  }

  // Otherwise, format the date
  const options = { month: 'short', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

/**
 * Validates API key format
 * @param {string} apiKey - The API key to validate
 * @returns {boolean} True if API key is valid
 */
function validateApiKey(apiKey) {
  // This is a simple validation, replace with actual validation logic
  return apiKey && apiKey.length > 8;
}

/**
 * Shows an error message
 * @param {string} message - The error message to display
 * @param {HTMLElement} container - The container to show the error in
 */
function showError(message, container) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.textContent = message;
  
  // Remove any existing error message
  const existingError = container.querySelector('.error-message');
  if (existingError) {
    container.removeChild(existingError);
  }
  
  container.appendChild(errorDiv);
}

// Export functions for use in other files
export {
  sendMessageToPlugin,
  formatDate,
  validateApiKey,
  showError
};
