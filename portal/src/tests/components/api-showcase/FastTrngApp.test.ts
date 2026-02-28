import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import FastTrngApp from '$lib/components/api-showcase/FastTrngApp.svelte';

vi.stubGlobal('IntersectionObserver', class {
    observe() { }
    unobserve() { }
    disconnect() { }
});

describe('FastTrngApp Showcase Component', () => {
    it('renders the core title and proof section', () => {
        const { getByText } = render(FastTrngApp);
        expect(getByText('Fast Edge-of-Chaos TRNG API')).toBeTruthy();
        expect(getByText('Live Audit Terminal')).toBeTruthy();
    });

    it('renders the interactive sample trigger', () => {
        const { getByText } = render(FastTrngApp);
        expect(getByText('Sample Vacuum')).toBeTruthy();
    });

    it('changes button text and starts sampling upon interaction', async () => {
        const { getByText } = render(FastTrngApp);

        const triggerBtn = getByText('Sample Vacuum');
        await fireEvent.click(triggerBtn);

        // button enters sampling state
        expect(getByText('Sampling...')).toBeTruthy();
    });
});
