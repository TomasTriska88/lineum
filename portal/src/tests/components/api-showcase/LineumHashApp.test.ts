import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import { tick } from 'svelte';
import LineumHashApp from '$lib/components/api-showcase/LineumHashApp.svelte';

vi.stubGlobal('IntersectionObserver', class {
    observe() { }
    unobserve() { }
    disconnect() { }
});

describe('LineumHashApp Showcase Component', () => {
    it('renders the core titles and proof section', () => {
        const { getByText } = render(LineumHashApp);
        expect(getByText('LineumHash API')).toBeTruthy();
        expect(getByText('Live Cryptographic Audit')).toBeTruthy();
        expect(getByText('Topological Hashing')).toBeTruthy(); // Head-to-head title
    });

    it('renders the interactive text input', () => {
        const { getByPlaceholderText } = render(LineumHashApp);
        expect(getByPlaceholderText('Enter string data to hash...')).toBeTruthy();
    });

    it('allows typing into the hash data input field', async () => {
        const { getByPlaceholderText } = render(LineumHashApp);

        const inputField = getByPlaceholderText('Enter string data to hash...') as HTMLInputElement;
        expect(inputField.value).toBe('Lineum is inevitable.');

        await fireEvent.input(inputField, { target: { value: 'Quantum Chaos' } });
        expect(inputField.value).toBe('Quantum Chaos');
    });
});
