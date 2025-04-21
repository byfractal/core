import React, { useState } from 'react';
import { Optimization, Project } from '@/types';
import { ProjectCard, NewProjectCard } from './project-card';
import { cn } from '@/lib/utils';

/**
 * Mock data for testing
 */
const MOCK_OPTIMIZATIONS: Optimization[] = [
  {
    id: '1',
    projectId: 'p1',
    title: 'Homepage Optimization',
    createdAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
    tags: [{ type: 'Layout' }, { type: 'Friction' }],
    status: 'completed',
  },
  {
    id: '2',
    projectId: 'p2',
    title: 'Checkout Flow',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(), // 3 hours ago
    tags: [{ type: 'Conversion' }, { type: 'Navigation' }],
    status: 'completed',
  },
  {
    id: '3',
    projectId: 'p3',
    title: 'Mobile Dashboard',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days ago
    tags: [{ type: 'Mobile' }, { type: 'Performance' }],
    status: 'completed',
  },
];

interface ProjectsPageProps {
  className?: string;
}

/**
 * ProjectsPage Component
 * 
 * Main entry point for user to see and manage optimization projects
 */
export const ProjectsPage: React.FC<ProjectsPageProps> = ({ className }) => {
  const [optimizations, setOptimizations] = useState<Optimization[]>(MOCK_OPTIMIZATIONS);
  
  // Handlers
  const handleSelectOptimization = (optimization: Optimization) => {
    console.log('Selected optimization:', optimization);
    // TODO: Navigate to the project detail page
  };
  
  const handleDeleteOptimization = (id: string) => {
    setOptimizations(prev => prev.filter(o => o.id !== id));
  };
  
  const handleDuplicateOptimization = (id: string) => {
    const original = optimizations.find(o => o.id === id);
    if (!original) return;
    
    const duplicate: Optimization = {
      ...original,
      id: `${id}-copy-${Date.now()}`,
      title: `${original.title} (Copy)`,
      createdAt: new Date().toISOString(),
    };
    
    setOptimizations(prev => [...prev, duplicate]);
  };
  
  const handleAddProject = () => {
    console.log('Add new project');
    // TODO: Navigate to new project creation flow
  };
  
  return (
    <div className={cn("flex flex-col w-full h-full p-6", className)}>
      {/* Heading */}
      <h1 className="text-3xl font-semibold text-figma-text-primary font-inter mb-2">
        Projects
      </h1>
      
      {/* Description */}
      <p className="text-figma-text-secondary font-inter text-sm mb-6">
        You can import data, analyze pages, and improve user experience based on real product insights.
      </p>
      
      {/* Projects Grid */}
      <div className="flex flex-col space-y-3 w-full">
        {/* New Project Card at the top */}
        <NewProjectCard onAddProject={handleAddProject} />
        
        {/* Existing Project Cards */}
        {optimizations.map(optimization => (
          <ProjectCard 
            key={optimization.id}
            optimization={optimization}
            onSelect={handleSelectOptimization}
            onDelete={handleDeleteOptimization}
            onDuplicate={handleDuplicateOptimization}
          />
        ))}
        
        {/* Empty state if no projects */}
        {optimizations.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 text-figma-text-secondary text-sm">
            <p>No optimizations yet.</p>
            <p>Create your first optimization to get started.</p>
          </div>
        )}
      </div>
    </div>
  );
}; 