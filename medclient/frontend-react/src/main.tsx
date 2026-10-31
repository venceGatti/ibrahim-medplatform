import React from 'react';
import { createRoot } from 'react-dom/client';
import { MedClientAppShell } from './implementations/MedClientAppShell';
import './styles.css';

export function mountMedClientApplication(rootElement: HTMLElement | null): void {
  if (!rootElement) {
    throw new Error('Elemento DOM radice #root assente: impossibile inizializzare MedClient React 19.');
  }
  const reactRoot = createRoot(rootElement);
  reactRoot.render(
    <React.StrictMode>
      <MedClientAppShell />
    </React.StrictMode>
  );
}

if (typeof document !== 'undefined') {
  const containerElement = document.getElementById('root');
  if (containerElement) {
    mountMedClientApplication(containerElement);
  }
}
