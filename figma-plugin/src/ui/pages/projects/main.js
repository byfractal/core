import { sendMessageToPlugin, formatDate } from '../../shared/utils.js';

// Initialize page
document.addEventListener('DOMContentLoaded', initProjectsPage);

/**
 * Initialize the projects page
 */
function initProjectsPage() {
  console.log('Projects page initialized');
  
  // Send message that UI is ready
  sendMessageToPlugin({ type: 'UI_READY' });
  
  // Request projects data
  sendMessageToPlugin({ type: 'GET_PROJECTS' });
  
  // Add event listener for "Add Project" button
  const addProjectBtn = document.querySelector('.add-project-btn');
  if (addProjectBtn) {
    addProjectBtn.addEventListener('click', handleAddProject);
  }
  
  // Listen for messages from the plugin
  window.onmessage = (event) => {
    const message = event.data.pluginMessage;
    if (!message) return;
    
    console.log('Message received from plugin:', message);
    
    switch (message.type) {
      case 'INIT_DATA':
        console.log('Initialized with version:', message.version);
        break;
        
      case 'PROJECTS_LOADED':
        renderProjects(message.projects);
        break;
        
      case 'PROJECT_SELECTED':
        console.log('Project selected:', message.projectName);
        break;
        
      case 'ERROR':
        console.error('Error:', message.message);
        break;
    }
  };
}

/**
 * Render the projects list
 * @param {Array} projects - The projects to render
 */
function renderProjects(projects) {
  const projectList = document.getElementById('project-list');
  const addProjectCard = projectList.querySelector('.add-project');
  
  // Remove all existing project cards except the "Add Project" card
  const existingProjects = projectList.querySelectorAll('.project-card:not(.add-project)');
  existingProjects.forEach(project => project.remove());
  
  // Add each project to the list
  projects.forEach(project => {
    const projectCard = document.createElement('div');
    projectCard.className = 'project-card';
    projectCard.dataset.projectId = project.id;
    
    projectCard.innerHTML = `
      <div class="project-info">
        <div class="project-icon">
          <!-- Document-cube icon to match Figma design -->
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 18H17V8H7V18Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 8V4H13L17 8H7Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13 15L10 12L11 11L13 13L17 9L18 10L13 15Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <div class="project-name">${project.name}</div>
          <div class="project-date">Edited ${formatDate(project.editedAt)}</div>
        </div>
      </div>
      <div class="arrow-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 6L15 12L9 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
    `;
    
    // Add click event listener to select project
    projectCard.addEventListener('click', () => {
      handleSelectProject(project.id, project.name);
    });
    
    // Add the project card before the "Add Project" card
    projectList.insertBefore(projectCard, addProjectCard);
  });
}

/**
 * Handle selecting a project
 * @param {string} projectId - The ID of the selected project
 * @param {string} projectName - The name of the selected project
 */
function handleSelectProject(projectId, projectName) {
  console.log('Selected project:', projectId, projectName);
  
  // Send message to plugin
  sendMessageToPlugin({
    type: 'SELECT_PROJECT',
    projectId,
    projectName
  });
}

/**
 * Handle adding a new project
 */
function handleAddProject() {
  console.log('Add new project');
  
  // Send message to plugin to navigate to import page
  sendMessageToPlugin({
    type: 'ADD_PROJECT'
  });
}
