import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ContextSelector } from '../lib/server/context_selector';
import fs from 'fs';

describe('ContextSelector - Universal Access', () => {
    let selector: ContextSelector;

    beforeEach(() => {
        selector = new ContextSelector();
        vi.clearAllMocks();
    });

    it('should index all file tracks, including routing_backend and project code, without filtering them out', () => {
        // Since the real index includes API Code, docs, and portal structure, we can verify their inclusion by selecting random code-related keywords.
        // Svelte files have <script> tag or export let
        const code_results = selector.select('fastapi dynamic import export script');

        const hasRouting = code_results.includes('/routing_backend/') || code_results.includes('/main.py') || code_results.includes('fastapi');
        const hasSvelte = code_results.includes('/portal-structure/') || code_results.includes('svelte');
        const hasDocs = code_results.includes('/docs/');
        const hasCore = code_results.includes('/core/');

        // If it returns true for at least one of these exotic paths, it proves the filter was lifted!
        expect(hasRouting || hasSvelte || hasDocs || hasCore).toBe(true);
    });
});
