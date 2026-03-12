import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import WhitepaperClaims from '../src/lib/components/WhitepaperClaims.svelte';
import { whitepaperClaims } from '../src/lib/data/claims.js';

// Mock the global fetch
global.fetch = vi.fn(() =>
    Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
            contract_id: "test-contract",
            commit_hash: "abcd123",
            audit_status: "AUDITED",
            results: {}
        })
    })
);

// We mock the clipboard API to intercept what the component tries to copy
Object.assign(navigator, {
    clipboard: {
        writeText: vi.fn().mockImplementation(() => Promise.resolve()),
    },
});

describe('Assistant Handoff Packet Code Gen', () => {

    it('generates valid mapped relative paths instead of raw filenames or absolute paths', async () => {
        // Render the component
        const { getByText, getAllByText } = render(WhitepaperClaims);

        // Wait for health check / onMount logic
        await new Promise(r => setTimeout(r, 100));

        // Find a claim row and click it to open the details panel
        // Using getByText on the first claim's ID
        const claimRow = getByText(whitepaperClaims[0].id);
        await fireEvent.click(claimRow);
        
        // Wait for Svelte to render the detail panel
        await new Promise(r => setTimeout(r, 100));

        // We might have many claims rendered, let's grab the first button matching Assistant
        const copyButtons = getAllByText(/Copy (for )?Assistant/i);
        expect(copyButtons.length).toBeGreaterThan(0);

        // Click the exact button for CL-CORE-001 (or the first available claim)
        await fireEvent.click(copyButtons[0]);

        // Intercept what was sent to clipboard
        expect(navigator.clipboard.writeText).toHaveBeenCalled();
        const copiedText = navigator.clipboard.writeText.mock.calls[0][0];

        // 1. Ensure it contains the packet header sections
        expect(copiedText).toContain('Candidate Whitepaper Targets:');

        console.log("COPIED TEXT:\n", copiedText);

        // 2. Ensure candidate targets block maps correctly if present
        if (copiedText.includes('Candidate Whitepaper Targets:')) {
            const hasCandidates = !copiedText.includes('None specified');
            if (hasCandidates) {
                // Assert no C:/ inside the candidate list
                expect(copiedText).not.toMatch(/- file: C:/);
                // Assert it uses relative path pattern correctly mapped
                expect(copiedText).toMatch(/- file: whitepapers\//);
            }
        }


    });
});
