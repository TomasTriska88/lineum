import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Improved ROOT detection: Walk up from __dirname to find the monorepo root
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

    // Fallback logic
    const fallback = path.resolve(__dirname, '../../');
    console.log(`[SYNC] findRoot falling back to: ${fallback}`);

    // If we're on Railway and whitepapers is missing, it's a configuration issue
    if (process.env.RAILWAY_ENVIRONMENT || fs.existsSync('/app')) {
        console.warn('\n' + '='.repeat(60));
        console.warn('[SYNC] DETECTED RESTRICTED BUILD CONTEXT');
        console.warn('[SYNC] The script cannot find whitepapers/ directory.');
        console.warn('[SYNC] ACTION REQUIRED: In Railway Dashboard, go to:');
        console.warn('[SYNC] Portal Service -> Settings -> General -> Root Directory');
        console.warn('[SYNC] Change it from "portal" to "./"');
        console.warn('='.repeat(60) + '\n');
    }

    return fallback;
}

const ROOT = findRoot(__dirname);
const DATA_TARGET = path.resolve(__dirname, '../src/lib/data');

const directoriesToSync = [
    { source: 'whitepapers', target: 'src/lib/data/whitepapers' },
    { source: 'source', target: 'static/data/source' }
];

function copyRecursiveSync(src, dest) {
    if (!fs.existsSync(src)) {
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
        fs.copyFileSync(src, dest);
    }
}

function sync() {
    console.log('[SYNC] Starting build-time data synchronization...');
    console.log(`[SYNC] ROOT determined as: ${ROOT}`);

    // Allow skipping sync for emergency builds or environments without data
    if (process.env.SKIP_SYNC === 'true') {
        console.log('[SYNC] SKIP_SYNC is true. Skipping data synchronization.');
        return;
    }

    // Diagnostic listing
    try {
        if (fs.existsSync(ROOT)) {
            const contents = fs.readdirSync(ROOT);
            console.log(`[SYNC] Contents of ROOT: ${contents.slice(0, 10).join(', ')}${contents.length > 10 ? '...' : ''}`);
        }
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

        if (fs.existsSync(targetPath)) {
            try {
                fs.rmSync(targetPath, { recursive: true, force: true });
            } catch (e) {
                console.warn(`[SYNC] Could not remove old directory ${targetPath}`);
            }
        }

        copyRecursiveSync(sourcePath, targetPath);

        const filesFound = fs.existsSync(targetPath) ? fs.readdirSync(targetPath) : [];
        console.log(`[SYNC] Success: Synced ${filesFound.length} items to ${targetPath}`);
    }

    // Final validation
    const wpTargetDir = path.join(path.resolve(__dirname, '../'), 'src/lib/data/whitepapers');
    const wpFound = fs.existsSync(wpTargetDir) ? fs.readdirSync(wpTargetDir).length : 0;

    if (wpFound === 0) {
        console.error('\n[SYNC] CRITICAL ERROR: Found 0 whitepapers in sync target.');
        console.error('[SYNC] This usually means Railway is only uploading the "portal" subdirectory.');
        console.error('[SYNC] Please check your Railway "Root Directory" setting.');
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
