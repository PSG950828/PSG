declare module 'react' {
  export function useState<T>(initial: T): [T, (value: T) => void];
  const React: any;
  export default React;
}

declare module 'react/jsx-runtime' {
  const jsxRuntime: any;
  export default jsxRuntime;
}

declare namespace React {
  interface FormEvent {
    preventDefault(): void;
  }
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
