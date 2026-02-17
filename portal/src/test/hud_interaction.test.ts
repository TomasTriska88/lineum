import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import { hudActive } from '../lib/stores/hudStore';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';
import { get } from 'svelte/store';

describe('HUD Store and Interaction', () => {
    it('should render ResonanceDeck and allow expansion', async () => {
        // Reset stores
        hudActive.set(true);

        render(ResonanceDeck, { props: { active: true } });

        const deck = screen.getByText('EXPAND EXPLORER');
        expect(deck).toBeDefined();

        await fireEvent.click(deck);

        expect(await screen.findByText('CLOSE')).toBeDefined();
        expect(await screen.findByText('Research Link Established')).toBeDefined();
    });
});
