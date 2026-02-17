import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Improved ROOT detection: Walk up from __dirname to find the monorepo root
function findRoot(startDir) {
    let current = startDir;
    while (current !== path.parse(current).root) {
        if (fs.existsSync(path.join(current, 'whitepapers'))) {
            return current;
        }
        current = path.dirname(current);
    }
    // Fallback to the previous logic if not found, but log it
    return path.resolve(__dirname, '../../');
}

const ROOT = findRoot(__dirname);
const DATA_TARGET = path.resolve(__dirname, '../src/lib/data');

const directoriesToSync = [
    { source: 'whitepapers', target: 'src/lib/data/whitepapers' },
    { source: 'source', target: 'static/data/source' }
];

function copyRecursiveSync(src, dest) {
    console.log(`[SYNC] Checking source: ${src}`);
    const exists = fs.existsSync(src);
    if (!exists) {
        console.warn(`[SYNC] Source DOES NOT exist: ${src}`);
        return;
    }
    const stats = fs.statSync(src);
    const isDirectory = stats.isDirectory();
    if (isDirectory) {
        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }
        fs.readdirSync(src).forEach((childItemName) => {
            copyRecursiveSync(path.join(src, childItemName), path.join(dest, childItemName));
        });
    } else {
        // Use copyFileSync for reliability
        fs.copyFileSync(src, dest);
    }
}

function sync() {
    console.log('[SYNC] Starting build-time data synchronization...');
    console.log(`[SYNC] CWD: ${process.cwd()}`);
    console.log(`[SYNC] ROOT determined as: ${ROOT}`);

    for (const { source, target } of directoriesToSync) {
        const sourcePath = path.join(ROOT, source);
        const targetPath = path.join(path.resolve(__dirname, '../'), target);

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

        // Log results
        const filesFound = fs.existsSync(targetPath) ? fs.readdirSync(targetPath) : [];
        console.log(`[SYNC] Success: Synced ${filesFound.length} items to ${targetPath}`);
        if (filesFound.length > 0) {
            console.log(`[SYNC] Items: ${filesFound.join(', ')}`);
        }
    }

    // Final validation: Fail the build if essential data is missing
    const wpTargetDir = path.join(path.resolve(__dirname, '../'), 'src/lib/data/whitepapers');
    if (!fs.existsSync(wpTargetDir) || fs.readdirSync(wpTargetDir).length === 0) {
        console.error('[SYNC] CRITICAL ERROR: Found 0 whitepapers in sync target. Build aborted.');
        process.exit(1);
    }

    console.log('[SYNC] Synchronization complete.');
}

try {
    sync();
} catch (err) {
    console.error('[SYNC] Critical error during synchronization:', err);
    process.exit(1);
}
