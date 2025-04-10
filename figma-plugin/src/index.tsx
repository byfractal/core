import React from 'react';
import ReactDOM from 'react-dom/client';
import { LoginPage } from './components/login';
import './styles.css';

// Simple wrapper pour le contenu
function App() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-white">
      <LoginPage />
    </div>
  );
}

// Montage direct de l'application
const root = document.getElementById('root');
if (root) {
  ReactDOM.createRoot(root).render(
    <App />
  );
} 