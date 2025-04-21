import React from 'react';

export function App() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-4">HCentric Interface</h2>
        <p className="mb-4">Using Clerk for authentication</p>
        <a href="./ui/ProjectsPage.html" className="inline-block px-4 py-2 bg-blue-500 text-white rounded">
          Access Projects
        </a>
      </div>
    </div>
  );
} 