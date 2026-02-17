import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';

describe('ResonanceDeck Basic Rendering', () => {
    it('should show the expand button', () => {
        render(ResonanceDeck, { active: true });
        screen.debug();
        expect(screen.getByText(/EXPAND EXPLORER/i)).toBeDefined();
    });
});
