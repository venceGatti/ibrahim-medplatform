import type {
  IIpcSidecarClient,
  IpcCircuitState,
  SidecarExecutionOutcome,
  SidecarHealthReport,
} from '../interfaces/engineContracts';

export interface SidecarClientConfig {
  readonly port: number;
  readonly ipcSecretToken: string;
  readonly hostAddress?: string;
  readonly maxRetries?: number;
  readonly baseBackoffMs?: number;
  readonly failureThreshold?: number;
  readonly cooldownPeriodMs?: number;
}

export class SidecarIpcClient implements IIpcSidecarClient {
  private readonly baseUrl: string;
  private readonly ipcSecretToken: string;
  private readonly maxRetries: number;
  private readonly baseBackoffMs: number;
  private readonly failureThreshold: number;
  private readonly cooldownPeriodMs: number;

  private circuitState: IpcCircuitState = 'CLOSED';
  private failureCount = 0;
  private openedTimestampMs = 0;

  public constructor(config: SidecarClientConfig) {
    const hostAddress = config.hostAddress ?? '127.0.0.1';
    if (hostAddress !== '127.0.0.1') {
      throw new Error(
        `SidecarIpcClient: Indirizzo loopback non consentito '${hostAddress}'. Deve essere rigorosamente 127.0.0.1 (ROA-08).`
      );
    }
    if (config.port <= 1024 || config.port > 65535) {
      throw new Error(`SidecarIpcClient: Porta effimera non valida ${config.port}`);
    }
    if (!config.ipcSecretToken || config.ipcSecretToken.trim().length === 0) {
      throw new Error('SidecarIpcClient: Token X-Tauri-IPC-Secret mancante o vuoto');
    }

    this.baseUrl = `http://127.0.0.1:${config.port}`;
    this.ipcSecretToken = config.ipcSecretToken;
    this.maxRetries = config.maxRetries ?? 3;
    this.baseBackoffMs = config.baseBackoffMs ?? 25;
    this.failureThreshold = config.failureThreshold ?? 3;
    this.cooldownPeriodMs = config.cooldownPeriodMs ?? 5000;
  }

  public currentCircuitState(): IpcCircuitState {
    if (
      this.circuitState === 'OPEN' &&
      Date.now() - this.openedTimestampMs >= this.cooldownPeriodMs
    ) {
      this.circuitState = 'HALF_OPEN';
    }
    return this.circuitState;
  }

  public consecutiveFailures(): number {
    return this.failureCount;
  }

  public computeBackoffDelayMs(attemptIndex: number): number {
    const exponent = Math.max(0, Math.min(8, attemptIndex));
    return this.baseBackoffMs * Math.pow(2, exponent);
  }

  private recordSuccess(): void {
    this.failureCount = 0;
    this.circuitState = 'CLOSED';
  }

  private recordFailure(): void {
    this.failureCount += 1;
    if (this.failureCount >= this.failureThreshold) {
      this.circuitState = 'OPEN';
      this.openedTimestampMs = Date.now();
    }
  }

  private async requestWithBackoff<T>(
    endpointPath: string,
    method: 'GET' | 'POST',
    jsonBody?: string
  ): Promise<T> {
    const activeCircuit = this.currentCircuitState();
    if (activeCircuit === 'OPEN') {
      throw new Error('Circuito IPC Sidecar APERTO per superamento soglia errori');
    }

    let lastCaughtError: Error = new Error('Richiesta IPC fallita');

    for (let attempt = 0; attempt <= this.maxRetries; attempt += 1) {
      try {
        const headersRecord: Record<string, string> = {
          'X-Tauri-IPC-Secret': this.ipcSecretToken,
          'Content-Type': 'application/json',
        };
        const httpResponse = await fetch(`${this.baseUrl}${endpointPath}`, {
          method,
          headers: headersRecord,
          body: jsonBody,
        });

        if (httpResponse.status === 403) {
          this.recordFailure();
          throw new Error('Autenticazione X-Tauri-IPC-Secret rifiutata (HTTP 403)');
        }

        if (!httpResponse.ok) {
          throw new Error(`Errore HTTP Sidecar: ${httpResponse.status}`);
        }

        const parsedResponse = (await httpResponse.json()) as T;
        this.recordSuccess();
        return parsedResponse;
      } catch (networkOrHttpError) {
        lastCaughtError =
          networkOrHttpError instanceof Error
            ? networkOrHttpError
            : new Error(String(networkOrHttpError));

        if (lastCaughtError.message.includes('HTTP 403')) {
          throw lastCaughtError;
        }

        if (attempt < this.maxRetries) {
          const delayMs = this.computeBackoffDelayMs(attempt);
          await new Promise<void>((resolveTimer) => {
            setTimeout(resolveTimer, delayMs);
          });
        }
      }
    }

    this.recordFailure();
    throw lastCaughtError;
  }

  public async checkHealth(): Promise<SidecarHealthReport> {
    return this.requestWithBackoff<SidecarHealthReport>('/agent/health', 'GET');
  }

  public async executeAction(
    actionType: string,
    actionParameters: Readonly<Record<string, unknown>>
  ): Promise<SidecarExecutionOutcome> {
    const serializedBody = JSON.stringify({
      action_type: actionType,
      action_parameters: actionParameters,
    });
    return this.requestWithBackoff<SidecarExecutionOutcome>(
      '/agent/execute',
      'POST',
      serializedBody
    );
  }
}
