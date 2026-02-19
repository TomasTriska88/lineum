import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Dialog from '$lib/components/ui/Dialog.svelte';

// Mock portal action since jsdom doesn't fully support moving nodes like this in test env easily
// or we can test it works by checking document.body
// But for unit test of component logic, we can mock it or just let it run.
// Let's try to let it run, but if it fails we mock.

describe('Dialog Component', () => {
    it('renders title and content', () => {
        const { getByText } = render(Dialog, {
            props: {
                title: 'Test Dialog',
                variant: 'info'
            }
        });

        expect(getByText('Test Dialog')).toBeTruthy();
    });

    it('emits confirm event on button click', async () => {
        const { getByText, component } = render(Dialog, {
            props: {
                title: 'Confirm Me',
                confirmLabel: 'Yes'
            }
        });

        const confirmBtn = getByText('Yes');
        const onConfirm = vi.fn();
        component.$on('confirm', onConfirm);

        await fireEvent.click(confirmBtn);
        expect(onConfirm).toHaveBeenCalled();
    });

    it('emits cancel event on button click', async () => {
        const { getByText, component } = render(Dialog, {
            props: {
                title: 'Cancel Me',
                cancelLabel: 'No',
                showCancel: true
            }
        });

        const cancelBtn = getByText('No');
        const onCancel = vi.fn();
        component.$on('cancel', onCancel);

        await fireEvent.click(cancelBtn);
        expect(onCancel).toHaveBeenCalled();
    });

    it('hides cancel button when showCancel is false', () => {
        const { queryByText } = render(Dialog, {
            props: {
                title: 'No Cancel',
                cancelLabel: 'Hidden',
                showCancel: false
            }
        });

        expect(queryByText('Hidden')).toBeNull();
    });

    it('applies danger variant styles', () => {
        const { container } = render(Dialog, {
            props: {
                title: 'Danger',
                variant: 'danger'
            }
        });

        // We check if the class was applied. 
        // Note: Portal moves it to body, so we need to look in document.body
        const dialogWindow = document.body.querySelector('.dialog-window');
        expect(dialogWindow?.classList.contains('danger')).toBe(true);
    });
});
