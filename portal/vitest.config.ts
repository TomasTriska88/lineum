import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
    plugins: [sveltekit()],
    test: {
        include: ['src/**/*.{test,spec}.{js,ts}'],
        exclude: ['src/tests/e2e/**', 'src/lib/data/**'],
        environment: 'jsdom',
        environmentOptions: {
            jsdom: {
                url: 'http://localhost/',
            }
        },
        globals: true,
        setupFiles: ['./src/tests/setup.ts']
    },
    resolve: {
        conditions: ['browser']
    }
});
