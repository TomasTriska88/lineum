import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, '../../');
const DATA_TARGET = path.resolve(__dirname, '../src/lib/data');

const directoriesToSync = [
    { source: 'whitepapers', target: 'whitepapers' },
    { source: 'source', target: 'source' }
];

function copyRecursiveSync(src, dest) {
    const exists = fs.existsSync(src);
    const stats = exists && fs.statSync(src);
    const isDirectory = exists && stats.isDirectory();
    if (isDirectory) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        fs.readdirSync(src).forEach((childItemName) => {
            copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
        });
    } else if (exists) {
        // Use copyFileSync for reliability
        fs.copyFileSync(src, dest);
    }
}

function sync() {
    console.log('[SYNC] Starting build-time data synchronization...');

    if (!fs.existsSync(DATA_TARGET)) {
        fs.mkdirSync(DATA_TARGET, { recursive: true });
    }

    for (const { source, target } of directoriesToSync) {
        const sourcePath = path.join(ROOT, source);
        const targetPath = path.join(DATA_TARGET, target);

        if (!fs.existsSync(sourcePath)) {
            console.warn(`[SYNC] Warning: Source directory not found: ${sourcePath}`);
            continue;
        }

        console.log(`[SYNC] Syncing ${source} -> ${targetPath}`);

        // Remove old to ensure clean sync
        if (fs.existsSync(targetPath)) {
            try {
                fs.rmSync(targetPath, { recursive: true, force: true });
            } catch (e) {
                console.warn(`[SYNC] Could not remove old directory ${targetPath}, attempting merge.`);
            }
        }

        copyRecursiveSync(sourcePath, targetPath);
    }

    console.log('[SYNC] Synchronization complete.');
}

try {
    sync();
} catch (err) {
    console.error('[SYNC] Critical error during synchronization:', err);
    process.exit(1);
}
