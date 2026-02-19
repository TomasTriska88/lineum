
import { vi, beforeAll } from 'vitest';

// GLOBAL SAFETY GUARD
// This file is loaded before tests to ensure no real API calls leak.
beforeAll(() => {
    // 1. Block Google Generative AI
    vi.mock('@google/generative-ai', () => ({
        GoogleGenerativeAI: vi.fn(() => ({
            getGenerativeModel: vi.fn(() => {
                throw new Error("⚠️ FATAL: GoogleGenerativeAI was accessed directly in a test environment!\nYOU MUST MOCK THIS DEPENDENCY to prevent burning real tokens.");
            })
        }))
    }));

    // 2. Poison the API Key
    vi.stubEnv('GEMINI_API_KEY', 'TEST_SAFE_KEY_DO_NOT_USE');

    // 3. Block Global Fetch (unless mocked)
    // We replace the global fetch with a guarded version
    const originalFetch = global.fetch;
    global.fetch = async (input, init) => {
        const url = input.toString();
        // Allow local API calls (mocked by SvelteKit usually, but good to be safe)
        if (url.startsWith('/') || url.includes('localhost')) {
            // Let it pass, but it should fail if server tries to call out
            return originalFetch(input, init);
        }

        // Allow data URIs and blobs
        if (url.startsWith('data:') || url.startsWith('blob:')) {
            return originalFetch(input, init);
        }

        // BLOCK EVERYTHING ELSE
        if (url.includes('google') || url.includes('googleapis') || url.includes('gemini')) {
            throw new Error(`⚠️ FATAL: External API call detected in test: ${url}\nYou must mock 'fetch' or the specific dependency.`);
        }

        return originalFetch(input, init) as Promise<Response>;
    };

    // 4. Mock Speech Synthesis (JSDOM doesn't have it)
    if (typeof window !== 'undefined') {
        const mockSpeechSynthesis = {
            cancel: vi.fn(),
            speak: vi.fn(),
            getVoices: () => [],
            pause: vi.fn(),
            resume: vi.fn(),
            paused: false,
            speaking: false,
            onvoiceschanged: null
        };
        Object.defineProperty(window, 'speechSynthesis', {
            value: mockSpeechSynthesis,
            writable: true
        });

        Object.defineProperty(window, 'SpeechSynthesisUtterance', {
            value: vi.fn(),
            writable: true
        });

        // Mock matchMedia
        Object.defineProperty(window, 'matchMedia', {
            writable: true,
            value: vi.fn().mockImplementation((query: string) => ({
                matches: false,
                media: query,
                onchange: null,
                addListener: vi.fn(), // deprecated
                removeListener: vi.fn(), // deprecated
                addEventListener: vi.fn(),
                removeEventListener: vi.fn(),
                dispatchEvent: vi.fn(),
            })),
        });

        // Mock Web Animations API
        const animateMock = vi.fn().mockReturnValue({
            finished: Promise.resolve(),
            cancel: vi.fn(),
            play: vi.fn(),
            pause: vi.fn(),
            reverse: vi.fn(),
            onfinish: null
        });

        Element.prototype.animate = animateMock;

        Object.defineProperty(HTMLElement.prototype, 'animate', {
            value: animateMock
        });

        Object.defineProperty(SVGElement.prototype, 'animate', {
            value: animateMock
        });
    }
});
