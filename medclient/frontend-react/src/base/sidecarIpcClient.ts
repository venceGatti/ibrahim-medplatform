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

  public async request<T>(
    endpointPath: string,
    method: 'GET' | 'POST',
    jsonBody?: string
  ): Promise<T> {
    return this.requestWithBackoff<T>(endpointPath, method, jsonBody);
  }

  public async checkHealth(): Promise<SidecarHealthReport> {
    return this.requestWithBackoff<SidecarHealthReport>('/agent/health', 'GET');
  }

  public async getClinicalSheet<T>(sheetId: string): Promise<T> {
    return this.requestWithBackoff<T>(`/api/v3/sheets/${encodeURIComponent(sheetId)}`, 'GET');
  }

  public async evaluateDiagnostic<T>(payload: unknown): Promise<T> {
    return this.requestWithBackoff<T>('/api/v3/engine/evaluate', 'POST', JSON.stringify(payload));
  }

  public async evaluatePharmacology<T>(
    payload: unknown,
    queryParams?: Readonly<Record<string, string | number | boolean>>
  ): Promise<T> {
    let targetEndpoint = '/api/v3/pharma/evaluate';
    if (queryParams) {
      const searchParams = new URLSearchParams();
      for (const [paramKey, paramValue] of Object.entries(queryParams)) {
        searchParams.append(paramKey, String(paramValue));
      }
      targetEndpoint += `?${searchParams.toString()}`;
    }
    return this.requestWithBackoff<T>(targetEndpoint, 'POST', JSON.stringify(payload));
  }

  public async evaluateExam<T>(payload: unknown): Promise<T> {
    return this.requestWithBackoff<T>('/api/v3/exam/evaluate', 'POST', JSON.stringify(payload));
  }

  public async searchHybrid<T>(queryText: string, limit = 10): Promise<T> {
    return this.requestWithBackoff<T>(
      '/api/v3/search/hybrid',
      'POST',
      JSON.stringify({ query_text: queryText, limit })
    );
  }

  public async scheduleFsrs<T>(payload: unknown): Promise<T> {
    return this.requestWithBackoff<T>('/api/v3/fsrs/schedule', 'POST', JSON.stringify(payload));
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

export function resolveSidecarIpcConfig(): SidecarClientConfig {
  let sidecarPort = 8765;
  let secretToken = 'medclient_local_session_secure_token';

  if (typeof window !== 'undefined') {
    const windowObj = window as unknown as Record<string, unknown>;
    if (typeof windowObj.__MEDCLIENT_SIDECAR_PORT__ === 'number') {
      sidecarPort = windowObj.__MEDCLIENT_SIDECAR_PORT__;
    }
    if (
      typeof windowObj.__TAURI_IPC_SECRET__ === 'string' &&
      windowObj.__TAURI_IPC_SECRET__.trim().length > 0
    ) {
      secretToken = windowObj.__TAURI_IPC_SECRET__;
    } else if (
      typeof windowObj.__MEDCLIENT_IPC_TOKEN__ === 'string' &&
      windowObj.__MEDCLIENT_IPC_TOKEN__.trim().length > 0
    ) {
      secretToken = windowObj.__MEDCLIENT_IPC_TOKEN__;
    }
  }

  return {
    port: sidecarPort,
    ipcSecretToken: secretToken,
    hostAddress: '127.0.0.1',
  };
}
