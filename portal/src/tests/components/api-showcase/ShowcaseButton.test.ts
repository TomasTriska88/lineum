import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import ShowcaseButton from '../../../lib/components/api-showcase/ShowcaseButton.svelte';

describe('ShowcaseButton', () => {
    it('renders idle state correctly', () => {
        const { getByText, getByRole } = render(ShowcaseButton, {
            status: 'idle',
            theme: 'sky',
            idleText: 'Run Idle',
            runningText: 'Is Running',
            doneText: 'Are Done'
        });

        expect(getByText('Run Idle')).toBeDefined();
        const button = getByRole('button');
        expect(button.className).toContain('text-sky-400');
    });

    it('renders running state correctly', () => {
        const { getByText, getByRole } = render(ShowcaseButton, {
            status: 'running',
            theme: 'emerald',
            idleText: 'Run Idle',
            runningText: 'Is Running',
            doneText: 'Are Done'
        });

        expect(getByText('Is Running')).toBeDefined();
        const button = getByRole('button');
        expect(button.className).toContain('text-emerald-400');
    });

    it('renders done state correctly', () => {
        const { getByText, getByRole } = render(ShowcaseButton, {
            status: 'done',
            theme: 'rose',
            idleText: 'Run Idle',
            runningText: 'Is Running',
            doneText: 'Are Done'
        });

        expect(getByText('Are Done')).toBeDefined();
        const button = getByRole('button');
        expect(button.className).toContain('border-rose-500/30');
    });

    // Note: dispatching events in raw testing-library without a wrapper component can be flaky in Svelte 4.
    // The button functionality is covered by E2E tests, so we omit the unit click dispatch test here.

    it('disables button when disabled prop is true', () => {
        const { getByRole } = render(ShowcaseButton, {
            status: 'idle',
            theme: 'sky',
            idleText: 'Run',
            runningText: 'Running',
            doneText: 'Done',
            disabled: true
        });

        const button = getByRole('button') as HTMLButtonElement;
        expect(button.disabled).toBe(true);
    });
});
