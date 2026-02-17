
import { describe, it, expect, vi } from 'vitest';

// Mock environment variables
vi.mock('$env/dynamic/private', () => ({
    env: { GEMINI_API_KEY: 'mock-key' }
}));

// Mock the raw imports if necessary, but try letting Vite handle it first.
// If this fails, we can add mocks for the markdown files.

import { SYSTEM_PROMPT } from '../lib/server/chat';

describe('System Prompt Configuration', () => {
    it('should include Lina Persona content', () => {
        // From LINA_PERSONA.md
        expect(SYSTEM_PROMPT).toContain("You are Lina");
        expect(SYSTEM_PROMPT).toContain("Identity & Tone");
        expect(SYSTEM_PROMPT).toContain("Model Scope & Epistemic Discipline");
    });

    it('should include Design Guide behavioral rules', () => {
        // From DESIGN_GUIDE.md
        expect(SYSTEM_PROMPT).toContain("FROM DESIGN GUIDE (BEHAVIORAL RULES):");
    });

    it('should include Project Context', () => {
        expect(SYSTEM_PROMPT).toContain("PROJECT CONTEXT (Context Window):");
        expect(SYSTEM_PROMPT).toContain("Lineum Core is a discrete simulation");
    });
});
