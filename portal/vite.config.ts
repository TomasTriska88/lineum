import { paraglide } from '@inlang/paraglide-sveltekit/vite'
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';
import { spawn, execSync } from 'child_process';
import path from 'path';

// Extract running commit for AGPL compliance footer
const getGitHash = () => {
	try {
		return execSync('git rev-parse --short HEAD').toString().trim();
	} catch (e) {
		return 'unknown';
	}
};

const autoSyncPlugin = () => ({
	name: 'auto-sync-data',
	configureServer(server: import('vite').ViteDevServer) {
		const watcher = server.watcher;
		const executeSync = () => {
			console.log('\x1b[36m[Auto-Sync]\x1b[0m Change detected in docs/source. Running sync-data.js...');
			const sync = spawn('node', ['scripts/sync-data.js'], { stdio: 'inherit' });
			sync.on('close', (code) => {
				if (code === 0) {
					console.log('\x1b[32m[Auto-Sync]\x1b[0m Sync complete. HMR will update AI Index.');
				} else {
					console.error('\x1b[31m[Auto-Sync]\x1b[0m Sync failed.');
				}
			});
		};

		// Watch specific folders relative to root
		watcher.add([
			path.resolve(__dirname, '../docs'),
			path.resolve(__dirname, '../hypotheses'),
			path.resolve(__dirname, '../whitepapers'),
			path.resolve(__dirname, '../whitepapers-legacy'),
			path.resolve(__dirname, 'LINA_PERSONA.md'),
			path.resolve(__dirname, 'COMMERCIAL_STRATEGY.md'),
			path.resolve(__dirname, 'ARCHITECTURE.md')
		]);

		watcher.on('change', (file: string) => {
			if (
				file.includes('whitepapers') ||
				file.includes('docs') ||
				file.includes('hypotheses') ||
				file.includes('LINA_PERSONA.md') ||
				file.includes('COMMERCIAL_STRATEGY.md') ||
				file.includes('ARCHITECTURE.md')
			) {
				executeSync();
			}
		});

		watcher.on('add', (file: string) => {
			if (file.includes('whitepapers') || file.includes('docs') || file.includes('hypotheses')) {
				executeSync();
			}
		});

		watcher.on('unlink', (file: string) => {
			if (file.includes('whitepapers') || file.includes('docs') || file.includes('hypotheses')) {
				executeSync();
			}
		});
	}
});

export default defineConfig({
	define: {
		__GIT_HASH__: JSON.stringify(getGitHash())
	},
	plugins: [paraglide({ project: './project.inlang', outdir: './src/lib/paraglide' }), sveltekit(), autoSyncPlugin()],
	server: {
		fs: {
			allow: ['..']
		}
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}', 'src/tests/**/*.{test,spec}.{js,ts}'],
		exclude: ['src/tests/e2e/**'],
		environment: 'jsdom',
		globals: true,
		setupFiles: ['src/tests/setup.ts'],
		fileParallelism: false
	}
});
