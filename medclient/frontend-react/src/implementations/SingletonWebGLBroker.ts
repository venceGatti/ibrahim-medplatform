import type { IWebGLContextBroker } from '../interfaces/engineContracts';

interface LoseContextExtension {
  loseContext: () => void;
}

export class SingletonWebGLBroker implements IWebGLContextBroker {
  private static singletonInstance: SingletonWebGLBroker | null = null;

  private currentOwnerId: string | null = null;
  private currentContext: WebGLRenderingContext | null = null;
  private currentPreemptCallback: (() => void) | null = null;
  private contextSwitchCounter = 0;

  public static getInstance(): SingletonWebGLBroker {
    if (!SingletonWebGLBroker.singletonInstance) {
      SingletonWebGLBroker.singletonInstance = new SingletonWebGLBroker();
    }
    return SingletonWebGLBroker.singletonInstance;
  }

  public acquireContext(
    ownerIdentifier: string,
    canvasElement: HTMLCanvasElement,
    onContextPreempted: () => void
  ): WebGLRenderingContext | null {
    if (!ownerIdentifier || ownerIdentifier.trim().length === 0) {
      throw new Error('SingletonWebGLBroker: ownerIdentifier non puo essere vuoto');
    }

    if (this.currentOwnerId && this.currentOwnerId !== ownerIdentifier) {
      this.forceLoseActiveContext();
      if (this.currentPreemptCallback) {
        const callbackToInvoke = this.currentPreemptCallback;
        this.currentPreemptCallback = null;
        callbackToInvoke();
      }
    }

    let acquiredGlContext: WebGLRenderingContext | null = null;
    try {
      const candidateContext =
        canvasElement.getContext('webgl') ??
        (canvasElement.getContext('experimental-webgl') as WebGLRenderingContext | null);
      acquiredGlContext = candidateContext;
    } catch (_webglUnsupportedError) {
      acquiredGlContext = null;
    }

    this.currentOwnerId = ownerIdentifier;
    this.currentContext = acquiredGlContext;
    this.currentPreemptCallback = onContextPreempted;
    this.contextSwitchCounter += 1;

    return acquiredGlContext;
  }

  public releaseContext(ownerIdentifier: string): void {
    if (this.currentOwnerId === ownerIdentifier) {
      this.forceLoseActiveContext();
      this.currentOwnerId = null;
      this.currentContext = null;
      this.currentPreemptCallback = null;
    }
  }

  public activeOwner(): string | null {
    return this.currentOwnerId;
  }

  public activeContextCount(): number {
    return this.currentOwnerId !== null ? 1 : 0;
  }

  public contextSwitchCount(): number {
    return this.contextSwitchCounter;
  }

  private forceLoseActiveContext(): void {
    if (this.currentContext && typeof this.currentContext.getExtension === 'function') {
      try {
        const loseExt = this.currentContext.getExtension(
          'WEBGL_lose_context'
        ) as LoseContextExtension | null;
        if (loseExt && typeof loseExt.loseContext === 'function') {
          loseExt.loseContext();
        }
      } catch (_extensionError) {
        // Estensione WEBGL_lose_context non supportata dall'ambiente corrente
      }
    }
  }
}
