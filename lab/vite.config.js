import { defineConfig } from 'vite'
import { svelte, vitePreprocess } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
    plugins: [svelte({ preprocess: vitePreprocess() })],
    define: {
        __GIT_HASH__: JSON.stringify('dev')
    },
    server: {
        fs: {
            allow: ['..']
        },
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
        port: 5174,
        host: '127.0.0.1',
        strictPort: true,
        watch: {
            ignored: ['**/output_wp/**', '**/.scratch/**']
        }
    },
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: [],
        exclude: ['tests/**', 'node_modules/**']
    }
})
