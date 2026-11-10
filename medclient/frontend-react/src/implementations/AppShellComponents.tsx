/**
 * Error boundary and sidecar status subcomponents for MedClientAppShell (keeps file < 350 lines).
 */
import React from 'react';

export interface ErrorBoundaryProps {
  readonly children: React.ReactNode;
}

export interface ErrorBoundaryState {
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

export interface SidecarStatusViewProps {
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

  if (errorMessage) {
    return (
      <div
        className="rounded-xl border border-rose-800/80 bg-rose-950/60 p-8 text-center text-rose-200"
        data-testid="sdui-error-indicator"
      >
        <h3 className="text-base font-bold text-white">Errore durante il caricamento di {title}</h3>
        <p className="mt-2 font-mono text-xs text-rose-300">{errorMessage}</p>
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-lg bg-rose-700 px-4 py-2 text-xs font-semibold text-white transition hover:bg-rose-600"
        >
          Riprova Richiesta IPC
        </button>
      </div>
    );
  }

  return null;
};
