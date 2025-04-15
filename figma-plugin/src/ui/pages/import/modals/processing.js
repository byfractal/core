/**
 * ProcessingModal class
 * Modal for showing data processing status
 */
export class ProcessingModal {
  constructor(importId) {
    this.modalContainer = document.getElementById('modal-container');
    this.importId = importId;
    this.currentStep = 0;
    this.totalSteps = 3;
    this.steps = [
      'Fetching analytics data...',
      'Processing user journey data...',
      'Analyzing UX patterns...'
    ];
    this.progressInterval = null;
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
        <h3 class="modal-title">Processing Data</h3>
        <button class="modal-close" id="processing-close" style="display: none;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="processing-animation">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
            <path d="M12 2V6M12 18V22M6 12H2M22 12H18M19.07 4.93L16.24 7.76M7.76 16.24L4.93 19.07M19.07 19.07L16.24 16.24M7.76 7.76L4.93 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="processing-status">
          <p id="processing-step">${this.steps[0]}</p>
          <div class="progress-bar">
            <div class="progress-fill" id="progress-fill" style="width: ${(1 / this.totalSteps) * 100}%;"></div>
          </div>
          <p class="progress-text"><span id="progress-percent">33</span>% complete</p>
        </div>
      </div>
      <div class="modal-footer" style="justify-content: center;">
        <p class="processing-note">This may take a few minutes. Please don't close the plugin.</p>
      </div>
    `;

    // Clear any existing modals
    this.modalContainer.innerHTML = '';
    this.modalContainer.appendChild(modal);
    this.modalContainer.classList.remove('hidden');

    // Add event listeners
    document.getElementById('processing-close').addEventListener('click', () => {
      this.hide();
    });

    // Start progress simulation
    this.simulateProgress();
  }

  /**
   * Hide the modal
   */
  hide() {
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
    }
    this.modalContainer.classList.add('hidden');
  }

  /**
   * Simulate progress for demonstration
   */
  simulateProgress() {
    this.progressInterval = setInterval(() => {
      if (this.currentStep < this.totalSteps - 1) {
        this.currentStep++;
        const progressPercent = Math.round(((this.currentStep + 1) / this.totalSteps) * 100);
        
        // Update UI
        document.getElementById('processing-step').textContent = this.steps[this.currentStep];
        document.getElementById('progress-fill').style.width = `${progressPercent}%`;
        document.getElementById('progress-percent').textContent = progressPercent;
      } else {
        // Final step complete
        clearInterval(this.progressInterval);
        
        // Simulate a small delay before automatically closing
        setTimeout(() => {
          this.hide();
        }, 1000);
      }
    }, 1500); // Adjust timing as needed
  }
}

// Styles needed for this component - will be injected via JavaScript
document.addEventListener('DOMContentLoaded', () => {
  const style = document.createElement('style');
  style.textContent = `
    .processing-animation {
      display: flex;
      justify-content: center;
      margin-bottom: 24px;
    }
    
    .spinner {
      animation: spin 2s linear infinite;
      color: #2563EB;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .processing-status {
      text-align: center;
    }
    
    .progress-bar {
      height: 8px;
      background-color: #E2E8F0;
      border-radius: 4px;
      margin: 16px 0;
      overflow: hidden;
    }
    
    .progress-fill {
      height: 100%;
      background-color: #2563EB;
      border-radius: 4px;
      transition: width 0.5s ease-in-out;
    }
    
    .progress-text {
      font-size: 14px;
      color: #64748B;
      margin: 0;
    }
    
    .processing-note {
      font-size: 12px;
      color: #94A3B8;
      margin: 0;
      text-align: center;
    }
  `;
  document.head.appendChild(style);
});
