import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Improved ROOT detection: Walk up from __dirname to find the monorepo root
function findRoot(startDir) {
    let current = startDir;
    console.log(`[SYNC] findRoot starting from: ${startDir}`);

    // Safety check for common environments
    const knownRoots = ['/app', process.cwd()];
    for (const kr of knownRoots) {
        if (fs.existsSync(path.join(kr, 'whitepapers'))) {
            console.log(`[SYNC] findRoot found known root: ${kr}`);
            return kr;
        }
    }

    while (true) {
        const checkPath = path.join(current, 'whitepapers');
        if (fs.existsSync(checkPath)) {
            return current;
        }
        const parent = path.dirname(current);
        if (parent === current) break; // Reached system root
        current = parent;
    }

    // Fallback: try to be smart about portal/scripts location
    const fallback = path.resolve(__dirname, '../../');
    console.log(`[SYNC] findRoot falling back to: ${fallback}`);
    return fallback;
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
    console.log(`[SYNC] __dirname: ${__dirname}`);
    console.log(`[SYNC] ROOT determined as: ${ROOT}`);

    // Diagnostic listing
    try {
        if (fs.existsSync('/app')) {
            console.log(`[SYNC] Contents of /app: ${fs.readdirSync('/app').join(', ')}`);
        }
        console.log(`[SYNC] Contents of ROOT: ${fs.readdirSync(ROOT).join(', ')}`);
    } catch (e) {
        console.warn(`[SYNC] Diagnostic listing failed: ${e.message}`);
    }

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
