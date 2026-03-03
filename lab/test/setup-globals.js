import { vi } from 'vitest';

// Global mocks for Node environment to prevent ReferenceErrors during module evaluation
if (typeof global.localStorage === 'undefined') {
    global.localStorage = {
        getItem: vi.fn().mockReturnValue(null),
        setItem: vi.fn(),
        clear: vi.fn(),
        removeItem: vi.fn(),
        length: 0,
        key: vi.fn()
    };
}

if (typeof global.navigator === 'undefined') {
    global.navigator = {
        language: 'en-US'
    };
}

// Mock window if needed since some Svelte components might check for it
if (typeof global.window === 'undefined') {
    global.window = global;
}

// Global and window fetch mock initialization
global.fetch = vi.fn();
if (typeof window !== 'undefined') {
    window.fetch = global.fetch;
}

// Mock ResizeObserver for JSDOM
class ResizeObserver {
    observe() { }
    unobserve() { }
    disconnect() { }
}
global.ResizeObserver = ResizeObserver;
if (typeof window !== 'undefined') {
    window.ResizeObserver = ResizeObserver;
}
