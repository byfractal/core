/**
 * SelectPageModal class
 * Modal for selecting Figma pages to analyze
 */
export class SelectPageModal {
  constructor() {
    this.modalContainer = document.getElementById('modal-container');
    this.selectedPages = [];
    this.onPageSelect = null; // Callback when pages are selected
    
    // Dummy pages for demonstration
    this.pages = [
      { id: 'page1', name: 'Landing Page', thumbnail: null },
      { id: 'page2', name: 'Dashboard', thumbnail: null },
      { id: 'page3', name: 'Settings', thumbnail: null },
      { id: 'page4', name: 'User Profile', thumbnail: null }
    ];
  }

  /**
   * Show the modal
   */
  show() {
    // Create modal content
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-header">
        <h3 class="modal-title">Select Pages to Analyze</h3>
        <button class="modal-close" id="select-page-close">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <p>Choose which pages you want to analyze for UX improvements.</p>
        <div class="pages-list" id="pages-list">
          ${this.renderPages()}
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="select-page-cancel">Cancel</button>
        <button class="btn btn-primary" id="select-page-confirm" disabled>Analyze Selected Pages</button>
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
  }

  /**
   * Add event listeners to modal elements
   */
  addEventListeners() {
    // Close button
    document.getElementById('select-page-close').addEventListener('click', () => {
      this.hide();
    });

    // Cancel button
    document.getElementById('select-page-cancel').addEventListener('click', () => {
      this.hide();
    });

    // Confirm button
    document.getElementById('select-page-confirm').addEventListener('click', () => {
      this.hide();
      if (this.onPageSelect) {
        this.onPageSelect(this.selectedPages);
      }
    });

    // Page checkboxes
    const pageCheckboxes = document.querySelectorAll('.page-checkbox');
    pageCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const pageId = e.target.dataset.pageId;
        const pageName = e.target.dataset.pageName;

        if (e.target.checked) {
          this.selectedPages.push({ id: pageId, name: pageName });
        } else {
          this.selectedPages = this.selectedPages.filter(page => page.id !== pageId);
        }

        // Enable/disable confirm button based on selection
        const confirmButton = document.getElementById('select-page-confirm');
        confirmButton.disabled = this.selectedPages.length === 0;
      });
    });
  }

  /**
   * Render the pages list
   * @returns {string} HTML for the pages list
   */
  renderPages() {
    return this.pages.map(page => `
      <div class="page-item">
        <div class="page-thumbnail">
          <!-- Placeholder thumbnail -->
          <div class="thumbnail-placeholder">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M4 18L8 14L10 16L15 11L20 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="page-details">
          <label class="page-name">${page.name}</label>
        </div>
        <div class="page-select">
          <input type="checkbox" class="page-checkbox" data-page-id="${page.id}" data-page-name="${page.name}" />
        </div>
      </div>
    `).join('');
  }
}

// Styles needed for this component - will be injected via JavaScript
// This is an alternative approach, but should be moved to CSS file in a more robust implementation
document.addEventListener('DOMContentLoaded', () => {
  const style = document.createElement('style');
  style.textContent = `
    .pages-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 16px;
      max-height: 300px;
      overflow-y: auto;
    }
    
    .page-item {
      display: flex;
      align-items: center;
      padding: 10px;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      background-color: white;
    }
    
    .page-thumbnail {
      width: 48px;
      height: 48px;
      background-color: #F1F5F9;
      border-radius: 4px;
      margin-right: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #64748B;
    }
    
    .page-details {
      flex: 1;
    }
    
    .page-name {
      font-size: 14px;
      font-weight: 500;
      color: #0F172A;
    }
    
    .page-select {
      margin-left: 12px;
    }
    
    .page-checkbox {
      width: 18px;
      height: 18px;
      cursor: pointer;
    }
  `;
  document.head.appendChild(style);
});
