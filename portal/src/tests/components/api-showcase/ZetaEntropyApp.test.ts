import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import ZetaEntropyApp from '$lib/components/api-showcase/ZetaEntropyApp.svelte';

vi.stubGlobal('IntersectionObserver', class {
    observe() { }
    unobserve() { }
    disconnect() { }
});

describe('ZetaEntropyApp Showcase Component', () => {
    it('renders the core title and descriptions', () => {
        const { getByText } = render(ZetaEntropyApp);
        expect(getByText('Extreme Zeta Entropy API')).toBeTruthy();
        expect(getByText('Live Audit Terminal')).toBeTruthy();
    });

    it('renders the interactive trigger button', () => {
        const { getByText, getByRole } = render(ZetaEntropyApp);
        const button = getByRole('button');
        expect(button.textContent).toContain('Stream Entropy');
    });

    it('changes button state upon interaction', async () => {
        const { getByRole } = render(ZetaEntropyApp);

        const triggerBtn = getByRole('button');
        await fireEvent.click(triggerBtn);

        expect(triggerBtn.textContent).toContain('Streaming...');
    });
});
