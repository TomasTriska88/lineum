import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
    plugins: [sveltekit()],
    test: {
        include: ['src/**/*.{test,spec}.{js,ts}'],
        exclude: ['src/tests/e2e/**'],
        environment: 'jsdom',
        globals: true,
        setupFiles: ['./src/tests/setup.ts']
    },
    resolve: {
        conditions: ['browser']
    }
});
