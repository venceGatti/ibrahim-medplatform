import React from 'react';
import { Power } from 'lucide-react';

interface ErrorBoundaryProps {
  readonly children: React.ReactNode;
}

interface ErrorBoundaryState {
  readonly hasError: boolean;
  readonly errorMessage: string;
}

export class ClinicalViewErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  public constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, errorMessage: '' };
  }

  public static getDerivedStateFromError(caughtError: Error): ErrorBoundaryState {
    return {
      hasError: true,
      errorMessage: caughtError.message,
    };
  }

  public render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <div
          className="rounded-lg border-2 border-red-600 bg-red-950 p-6 text-red-100"
          data-testid="sdui-error-boundary-fallback"
        >
          <h3 className="text-base font-bold">
            An unexpected error occurred in this view
          </h3>
          <p className="mt-2 font-mono text-xs text-red-200">{this.state.errorMessage}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

interface SidecarStatusViewProps {
  readonly title: string;
  readonly isLoading: boolean;
  readonly errorMessage: string | null;
  readonly onRetry: () => void;
}

export const SidecarStatusView: React.FC<SidecarStatusViewProps> = ({
  title,
  isLoading,
  errorMessage,
  onRetry,
}) => {
  if (isLoading) {
    return (
      <div
        className="flex flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 p-12 text-center"
        data-testid="sdui-loading-indicator"
      >
        <div className="mb-4 h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        <h3 className="text-sm font-bold text-white">Caricamento {title} in corso...</h3>
        <p className="mt-1 text-xs text-slate-400">
          Interrogazione del Sidecar clinico locale su{' '}
          <code className="rounded bg-slate-800 px-1 py-0.5 font-mono text-blue-300">
            http://127.0.0.1:8765
          </code>
        </p>
      </div>
    );
  }

  return (
    <div
      className="rounded-xl border border-amber-600/60 bg-amber-950/30 p-6 text-amber-100"
      data-testid="sdui-offline-indicator"
    >
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-amber-900/60 p-2 text-amber-400">
          <Power className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-bold text-amber-200">
            Sidecar Clinico Locale Non Raggiungibile
          </h3>
          <p className="mt-1 text-xs text-amber-300/80">
            Impossibile recuperare i dati per <span className="font-semibold text-white">{title}</span>.
            Verificare che il runtime FastAPI sia attivo su 127.0.0.1:8765 con l&apos;header X-Tauri-IPC-Secret.
          </p>
          {errorMessage && (
            <p className="mt-2 rounded bg-black/40 p-2 font-mono text-xs text-red-300">
              {errorMessage}
            </p>
          )}
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 rounded bg-amber-600 px-3 py-1.5 text-xs font-semibold text-slate-950 hover:bg-amber-500 transition"
            data-testid="sdui-retry-connection-button"
          >
            Riprova Connessione
          </button>
        </div>
      </div>
    </div>
  );
};
