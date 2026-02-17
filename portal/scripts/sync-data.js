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
    { source: 'hypotheses', target: 'src/lib/data/hypotheses' },
    { source: 'source', target: 'static/data/source' }
];

const coreFilesToSync = [
    { source: 'lineum.py', target: 'src/lib/data/core/lineum.py' },
    { source: 'tools/whitepaper_check.py', target: 'src/lib/data/core/whitepaper_check.py' },
    { source: 'tools/whitepaper_contract.py', target: 'src/lib/data/core/whitepaper_contract.py' }
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
        const destDir = path.dirname(dest);
        if (!fs.existsSync(destDir)) {
            fs.mkdirSync(destDir, { recursive: true });
        }
        fs.copyFileSync(src, dest);
    }
}

function extractMetadata(content, filePath) {
    const fileName = path.basename(filePath);
    let status = 'Current';

    if (filePath.includes('hypotheses')) {
        status = 'Hypothesis';
    }

    // Look for [STATUS: ...] or # STATUS: ...
    const statusMatch = content.match(/\[STATUS:\s*([^\]]+)\]/i) || content.match(/#\s*STATUS:\s*([^\r\n]+)/i);
    if (statusMatch) {
        status = statusMatch[1].trim();
    }

    return {
        name: fileName,
        path: filePath.replace(ROOT, '').replace(/\\/g, '/'),
        status: status,
        type: fileName.endsWith('.md') ? 'documentation' : 'code'
    };
}

function generateAiIndex(targetDir) {
    console.log('[SYNC] Generating AI Index...');
    const index = [];
    const sourceDirs = [
        path.join(targetDir, 'whitepapers'),
        path.join(targetDir, 'hypotheses'),
        path.join(targetDir, 'core'),
        path.join(path.resolve(__dirname, '../src/lib')), // Include portal logic
    ];

    const processDir = (dir) => {
        if (!fs.existsSync(dir)) return;
        const items = fs.readdirSync(dir);
        for (const item of items) {
            const fullPath = path.join(dir, item);
            if (fs.statSync(fullPath).isDirectory()) {
                if (!['node_modules', '.svelte-kit', 'build', 'data'].includes(item)) {
                    processDir(fullPath);
                }
            } else if (['.md', '.js', '.ts', '.svelte', '.py'].some(ext => item.endsWith(ext))) {
                const content = fs.readFileSync(fullPath, 'utf8');
                // Basic security: skip if it looks like it contains keys (very crude check)
                if (content.includes('AIzaSy')) continue; // Don't index the actual API keys if they leaked into files

                index.push({
                    ...extractMetadata(content, fullPath),
                    content: content
                });
            }
        }
    };

    sourceDirs.forEach(processDir);

    fs.writeFileSync(
        path.join(targetDir, 'ai_index.json'),
        JSON.stringify(index, null, 2)
    );
    console.log(`[SYNC] AI Index generated with ${index.length} files.`);
}

function sync() {
    console.log('[SYNC] Starting build-time data synchronization...');
    console.log(`[SYNC] ROOT determined as: ${ROOT}`);

    if (process.env.SKIP_SYNC === 'true') {
        console.log('[SYNC] SKIP_SYNC is true. Skipping data synchronization.');
        return;
    }

    // Sync directories
    for (const { source, target } of directoriesToSync) {
        const sourcePath = path.join(ROOT, source);
        const targetPath = path.join(path.resolve(__dirname, '../'), target);

        if (!fs.existsSync(sourcePath)) {
            console.warn(`[SYNC] Warning: Source directory not found: ${sourcePath}`);
            continue;
        }

        console.log(`[SYNC] Syncing ${source} -> ${targetPath}`);
        if (fs.existsSync(targetPath)) {
            fs.rmSync(targetPath, { recursive: true, force: true });
        }
        copyRecursiveSync(sourcePath, targetPath);
    }

    // Sync individual core files
    for (const { source, target } of coreFilesToSync) {
        const sourcePath = path.join(ROOT, source);
        const targetPath = path.join(path.resolve(__dirname, '../'), target);

        if (fs.existsSync(sourcePath)) {
            console.log(`[SYNC] Syncing core file: ${source} -> ${targetPath}`);
            copyRecursiveSync(sourcePath, targetPath);
        }
    }

    // Generate AI Index
    generateAiIndex(DATA_TARGET);

    console.log('[SYNC] Synchronization complete.');
}

try {
    sync();
} catch (err) {
    console.error('[SYNC] Critical error during synchronization:', err);
    process.exit(1);
}
