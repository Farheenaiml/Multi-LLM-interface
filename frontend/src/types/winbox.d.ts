declare module 'winbox' {
  interface WinBoxOptions {
    title?: string;
    width?: number | string;
    height?: number | string;
    x?: number | string;
    y?: number | string;
    root?: HTMLElement;
    class?: string[];
    html?: string;
    onclose?: () => boolean | void;
    onresize?: (width: number, height: number) => void;
    onmove?: (x: number, y: number) => void;
    onfocus?: () => void;
    onblur?: () => void;
    [key: string]: any;
  }

  interface WinBoxConstructor {
    new (options?: WinBoxOptions): WinBoxInstance;
  }

  interface WinBoxInstance {
    body: HTMLElement;
    close(): void;
    minimize(): void;
    maximize(): void;
    restore(): void;
    resize(width?: number, height?: number): void;
    move(x?: number, y?: number): void;
    focus(): void;
    blur(): void;
    setTitle(title: string): void;
    addClass(className: string): void;
    removeClass(className: string): void;
  }

  const WinBox: WinBoxConstructor;
  export = WinBox;
}