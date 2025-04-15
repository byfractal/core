import { sendMessageToPlugin, validateApiKey, showError } from '../../shared/utils.js';
import { SelectPageModal } from './modals/select-page.js';
import { ProcessingModal } from './modals/processing.js';
import { ImprovementsModal } from './modals/improvements.js';

// Initialize page when DOM is loaded
document.addEventListener('DOMContentLoaded', initImportPage);

/**
 * Initialize the import page
 */
function initImportPage() {
  console.log('Import page initialized');
  
  // Send message that UI is ready
  sendMessageToPlugin({ type: 'UI_READY' });
  
  // Initialize form elements
  setupAPIKeyToggle();
  setupDatePickers();
  
  // Add event listeners
  document.getElementById('back-to-projects').addEventListener('click', navigateToProjects);
  document.getElementById('import-form').addEventListener('submit', handleFormSubmit);
  document.getElementById('install-extension-btn').addEventListener('click', handleInstallExtension);
  
  // Listen for messages from the plugin
  window.onmessage = (event) => {
    const message = event.data.pluginMessage;
    if (!message) return;
    
    console.log('Message received from plugin:', message);
    
    switch (message.type) {
      case 'IMPORT_STARTED':
        console.log('Import started with ID:', message.importId);
        showProcessingModal(message.importId);
        break;
        
      case 'IMPORT_COMPLETE':
        console.log('Import completed with ID:', message.importId);
        showImprovementsModal(message.importId);
        break;
        
      case 'ERROR':
        console.error('Error:', message.message);
        // If there's an active modal, close it
        document.getElementById('modal-container').classList.add('hidden');
        break;
    }
  };
}

/**
 * Setup the API key toggle visibility
 */
function setupAPIKeyToggle() {
  const toggleButton = document.getElementById('toggle-api-key-visibility');
  const apiKeyInput = document.getElementById('api-key');
  
  toggleButton.addEventListener('click', () => {
    const currentType = apiKeyInput.type;
    apiKeyInput.type = currentType === 'password' ? 'text' : 'password';
    
    // Update the icon (optional enhancement)
    const eyeIcon = toggleButton.querySelector('svg');
    if (apiKeyInput.type === 'text') {
      eyeIcon.innerHTML = `
        <path d="M3.5 7.5C4.45846 8.09095 6.25499 9.5 8 9.5C9.74501 9.5 11.5415 8.09095 12.5 7.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M1 5L2.5 7.5M15 5L13.5 7.5M7 13L8 10.5M9 13L8 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      `;
    } else {
      eyeIcon.innerHTML = `
        <path d="M2 8C2 8 4.00003 3.5 8 3.5C11.9999 3.5 14 8 14 8C14 8 11.9999 12.5 8 12.5C4.00003 12.5 2 8 2 8Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M8 9.5C8.82843 9.5 9.5 8.82843 9.5 8C9.5 7.17157 8.82843 6.5 8 6.5C7.17157 6.5 6.5 7.17157 6.5 8C6.5 8.82843 7.17157 9.5 8 9.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      `;
    }
  });
}

/**
 * Setup the date pickers
 */
function setupDatePickers() {
  // Start date picker
  const startDateInput = document.getElementById('start-date');
  const startDateDisplay = document.getElementById('start-date-display');
  
  startDateInput.addEventListener('change', (e) => {
    const date = new Date(e.target.value);
    startDateDisplay.textContent = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    startDateDisplay.classList.add('has-value');
  });
  
  // End date picker
  const endDateInput = document.getElementById('end-date');
  const endDateDisplay = document.getElementById('end-date-display');
  
  endDateInput.addEventListener('change', (e) => {
    const date = new Date(e.target.value);
    endDateDisplay.textContent = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    endDateDisplay.classList.add('has-value');
  });
  
  // Set default dates (last 30 days)
  const today = new Date();
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(today.getDate() - 30);
  
  // Format dates to YYYY-MM-DD for input value
  startDateInput.value = formatDateForInput(thirtyDaysAgo);
  endDateInput.value = formatDateForInput(today);
  
  // Trigger change events to update display
  startDateInput.dispatchEvent(new Event('change'));
  endDateInput.dispatchEvent(new Event('change'));
}

/**
 * Format date for date input value (YYYY-MM-DD)
 * @param {Date} date - The date to format
 * @returns {string} Formatted date string
 */
function formatDateForInput(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Handle form submission
 * @param {Event} e - The form submit event
 */
function handleFormSubmit(e) {
  e.preventDefault();
  
  const apiKey = document.getElementById('api-key').value;
  const startDate = document.getElementById('start-date').value;
  const endDate = document.getElementById('end-date').value;
  
  // Validate form
  if (!validateApiKey(apiKey)) {
    showError('Please enter a valid API key', e.target);
    return;
  }
  
  if (!startDate || !endDate) {
    showError('Please select a date range', e.target);
    return;
  }
  
  // Format the date range for display
  const dateRange = {
    startDate,
    endDate,
    displayText: `${new Date(startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${new Date(endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`
  };
  
  // Show select page modal first
  showSelectPageModal(apiKey, dateRange);
}

/**
 * Navigate back to projects page
 */
function navigateToProjects() {
  sendMessageToPlugin({ type: 'NAVIGATE_TO_PROJECTS' });
}

/**
 * Handle install extension button click
 */
function handleInstallExtension() {
  sendMessageToPlugin({ type: 'INSTALL_EXTENSION' });
}

/**
 * Show the select page modal
 * @param {string} apiKey - The API key
 * @param {Object} dateRange - The date range object
 */
function showSelectPageModal(apiKey, dateRange) {
  const selectPageModal = new SelectPageModal();
  selectPageModal.show();
  
  // When a page is selected, start the import process
  selectPageModal.onPageSelect = (selectedPages) => {
    console.log('Selected pages:', selectedPages);
    
    // Start the import process
    sendMessageToPlugin({
      type: 'IMPORT_DATA',
      apiKey,
      dateRange,
      selectedPages
    });
  };
}

/**
 * Show the processing modal
 * @param {string} importId - The import ID
 */
function showProcessingModal(importId) {
  const processingModal = new ProcessingModal(importId);
  processingModal.show();
}

/**
 * Show the improvements modal
 * @param {string} importId - The import ID
 */
function showImprovementsModal(importId) {
  const improvementsModal = new ImprovementsModal(importId);
  improvementsModal.show();
  
  // When the modal is closed, send import complete message
  improvementsModal.onClose = () => {
    sendMessageToPlugin({
      type: 'IMPORT_COMPLETE',
      importId
    });
  };
}
