/**
 * ImprovementsModal class
 * Modal for displaying UX/UI improvement recommendations
 */
export class ImprovementsModal {
  constructor(importId) {
    this.modalContainer = document.getElementById('modal-container');
    this.importId = importId;
    this.onClose = null; // Callback when the modal is closed
    
    // Sample improvements data - in a real implementation, this would come from the plugin
    this.improvements = [
      {
        id: 'imp_001',
        title: 'Improve call-to-action contrast',
        description: 'The primary CTA buttons have insufficient contrast ratio (2.5:1). Increase to at least 4.5:1 for better accessibility.',
        severity: 'high',
        location: 'Landing Page'
      },
      {
        id: 'imp_002',
        title: 'Reduce form field count',
        description: 'Sign-up form has 8 fields, which is causing a 40% drop-off rate. Consider reducing to essential fields only.',
        severity: 'medium',
        location: 'Sign Up Modal'
      },
      {
        id: 'imp_003',
        title: 'Increase touch target size',
        description: 'Mobile menu items are too small (24x24px). Increase to at least 44x44px for better usability on touch devices.',
        severity: 'medium', 
        location: 'Mobile Navigation'
      }
    ];
  }

  /**
   * Show the modal
   */
  show() {
    // Create modal content
    const modal = document.createElement('div');
    modal.className = 'modal improvements-modal';
    modal.innerHTML = `
      <div class="modal-header">
        <h3 class="modal-title">Improvement Recommendations</h3>
        <button class="modal-close" id="improvements-close">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="improvements-summary">
          <div class="summary-item">
            <div class="summary-number">${this.improvements.length}</div>
            <div class="summary-label">Improvements</div>
          </div>
          <div class="summary-item">
            <div class="summary-number">${this.getImprovementsBySeverity('high').length}</div>
            <div class="summary-label">High Priority</div>
          </div>
          <div class="summary-item">
            <div class="summary-number">${this.getImprovementsBySeverity('medium').length}</div>
            <div class="summary-label">Medium Priority</div>
          </div>
        </div>
        
        <div class="improvements-list">
          ${this.renderImprovements()}
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="export-improvements">Export Report</button>
        <button class="btn btn-primary" id="apply-improvements">Apply to Design</button>
      </div>
    `;

    // Clear any existing modals
    this.modalContainer.innerHTML = '';
    this.modalContainer.appendChild(modal);
    this.modalContainer.classList.remove('hidden');

    // Add event listeners
    this.addEventListeners();
  }

  /**
   * Hide the modal
   */
  hide() {
    this.modalContainer.classList.add('hidden');
    if (this.onClose) {
      this.onClose();
    }
  }

  /**
   * Add event listeners to modal elements
   */
  addEventListeners() {
    // Close button
    document.getElementById('improvements-close').addEventListener('click', () => {
      this.hide();
    });

    // Export button
    document.getElementById('export-improvements').addEventListener('click', () => {
      alert('Export functionality would be implemented here');
    });

    // Apply improvements button
    document.getElementById('apply-improvements').addEventListener('click', () => {
      alert('Apply improvements functionality would be implemented here');
      this.hide();
    });
  }

  /**
   * Get improvements filtered by severity
   * @param {string} severity - The severity level to filter by
   * @returns {Array} Filtered improvements
   */
  getImprovementsBySeverity(severity) {
    return this.improvements.filter(improvement => improvement.severity === severity);
  }

  /**
   * Render the improvements list
   * @returns {string} HTML for the improvements list
   */
  renderImprovements() {
    return this.improvements.map(improvement => `
      <div class="improvement-item severity-${improvement.severity}">
        <div class="improvement-header">
          <div class="improvement-severity">${this.getSeverityLabel(improvement.severity)}</div>
          <div class="improvement-location">${improvement.location}</div>
        </div>
        <h4 class="improvement-title">${improvement.title}</h4>
        <p class="improvement-description">${improvement.description}</p>
        <div class="improvement-actions">
          <button class="btn-link">Ignore</button>
          <button class="btn-link">Show in Design</button>
        </div>
      </div>
    `).join('');
  }

  /**
   * Get a formatted label for a severity level
   * @param {string} severity - The severity level
   * @returns {string} Formatted label
   */
  getSeverityLabel(severity) {
    switch (severity) {
      case 'high':
        return 'High Priority';
      case 'medium':
        return 'Medium Priority';
      case 'low':
        return 'Low Priority';
      default:
        return 'Priority';
    }
  }
}

// Styles needed for this component - will be injected via JavaScript
document.addEventListener('DOMContentLoaded', () => {
  const style = document.createElement('style');
  style.textContent = `
    .improvements-modal {
      max-width: 450px;
    }
    
    .improvements-summary {
      display: flex;
      justify-content: space-between;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid #E2E8F0;
    }
    
    .summary-item {
      text-align: center;
      flex: 1;
    }
    
    .summary-number {
      font-size: 24px;
      font-weight: 600;
      color: #0F172A;
    }
    
    .summary-label {
      font-size: 12px;
      color: #64748B;
      margin-top: 4px;
    }
    
    .improvements-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
      max-height: 300px;
      overflow-y: auto;
    }
    
    .improvement-item {
      padding: 16px;
      border-radius: 6px;
      border-left: 4px solid #CBD5E1;
      background-color: #F8FAFC;
    }
    
    .improvement-item.severity-high {
      border-color: #EF4444;
    }
    
    .improvement-item.severity-medium {
      border-color: #F97316;
    }
    
    .improvement-item.severity-low {
      border-color: #3B82F6;
    }
    
    .improvement-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    
    .improvement-severity {
      font-size: 12px;
      font-weight: 500;
    }
    
    .severity-high .improvement-severity {
      color: #EF4444;
    }
    
    .severity-medium .improvement-severity {
      color: #F97316;
    }
    
    .severity-low .improvement-severity {
      color: #3B82F6;
    }
    
    .improvement-location {
      font-size: 12px;
      color: #64748B;
    }
    
    .improvement-title {
      font-size: 14px;
      font-weight: 600;
      color: #0F172A;
      margin: 0 0 8px 0;
    }
    
    .improvement-description {
      font-size: 13px;
      color: #64748B;
      margin: 0 0 12px 0;
      line-height: 1.5;
    }
    
    .improvement-actions {
      display: flex;
      justify-content: flex-end;
      gap: 16px;
    }
    
    .btn-link {
      background: none;
      border: none;
      color: #2563EB;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      padding: 0;
    }
    
    .btn-link:hover {
      text-decoration: underline;
    }
  `;
  document.head.appendChild(style);
});
