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

    // Check for Railway Staged Assets
    const stagedPath = path.join(startDir, '../railway_assets'); // Assuming startDir is scripts/
    if (fs.existsSync(stagedPath)) {
        console.log(`[SYNC] Detected Railway Staged Assets at: ${stagedPath}`);
        return stagedPath;
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

        // Final check for staged assets in current dir if structure is flat
        // On railway, root might be ./ and assets might be in ./railway_assets
        if (fs.existsSync(path.join(process.cwd(), 'railway_assets'))) {
            console.log('[SYNC] Found railway_assets in CWD. Using that.');
            return path.join(process.cwd(), 'railway_assets');
        }

        console.warn('[SYNC] The script cannot find whitepapers/ directory.');
        console.warn('[SYNC] POSSIBLE CAUSE: Service Name Mismatch or Assets not staged.');
        console.warn('[SYNC] ACTION REQUIRED:');
        console.warn('[SYNC] 1. Rename your service to "Portal" (or "portal") in Railway Dashboard.');
        console.warn('[SYNC] 2. OR Manually set Root Directory to "./" in Settings -> General.');
        console.warn('[SYNC] 3. OR Ensure "npm run stage" was run and committed.');
        console.warn('='.repeat(60) + '\n');
    }

    return fallback;
}

const ROOT = findRoot(__dirname);
const DATA_TARGET = path.resolve(__dirname, '../src/lib/data');

const directoriesToSync = [
    { source: 'whitepapers', target: 'src/lib/data/whitepapers' },
    { source: 'hypotheses', target: 'src/lib/data/hypotheses' },
    { source: 'whitepaper-old', target: 'src/lib/data/whitepapers-legacy' }, // Added Legacy
    { source: 'source', target: 'static/data/source' },
    { source: '.agent/workflows', target: 'src/lib/data/workflows' }, // Added Operational Knowledge
    { source: 'portal/src/routes', target: 'src/lib/data/portal-structure' } // Added Site Structure
];

const coreFilesToSync = [
    { source: 'lineum.py', target: 'src/lib/data/core/lineum.py' },
    { source: 'tools/whitepaper_check.py', target: 'src/lib/data/core/whitepaper_check.py' },
    { source: 'tools/whitepaper_contract.py', target: 'src/lib/data/core/whitepaper_contract.py' },
    // Persona & Design (Active Prompt Source)
    { source: 'portal/LINA_PERSONA.md', target: 'src/lib/data/core/LINA_PERSONA.md' },
    { source: 'portal/DESIGN_GUIDE.md', target: 'src/lib/data/core/DESIGN_GUIDE.md' }
];

const projectFilesToSync = [
    { source: 'README.md', target: 'src/lib/data/project/README.md' },
    { source: 'LICENSE', target: 'src/lib/data/project/LICENSE' },
    { source: '.agent/rules.md', target: 'src/lib/data/project/rules.md' },
    { source: 'todo.md', target: 'src/lib/data/project/todo.md' },
    { source: 'lab/README.md', target: 'src/lib/data/project/lab_readme.md' },
    { source: 'CITATION.cff', target: 'src/lib/data/project/CITATION.cff' },
    { source: '.zenodo.json', target: 'src/lib/data/project/zenodo.json' },
    { source: 'railway.json', target: 'src/lib/data/project/railway_config.json' },
    { source: 'requirements.txt', target: 'src/lib/data/project/requirements.txt' },
    { source: 'portal/package.json', target: 'src/lib/data/project/portal_package.json' }
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
    let track = 'other';

    if (filePath.includes('hypotheses')) {
        status = 'Hypothesis';
    } else if (filePath.includes('whitepapers-legacy')) {
        status = 'LEGACY / UNRELIABLE'; // Explicit warning
    } else if (filePath.includes('whitepapers')) {
        if (fileName.startsWith('lineum-core')) {
            track = 'core';
        } else if (fileName.startsWith('lineum-exp')) {
            track = 'exp';
            status = 'EXPERIMENTAL / OUT OF CORE SCOPE — do not treat as VALIDATED';
        } else if (fileName.startsWith('lineum-extension')) {
            track = 'extension';
            status = 'EXTENSION / OUT OF CORE SCOPE — do not treat as VALIDATED';
        }
    } else if (filePath.includes('project')) {
        status = 'Project Context';
    } else if (filePath.includes('workflows')) {
        status = 'Operational Knowledge';
    } else if (filePath.includes('portal-structure')) {
        status = 'Site Structure';
    }

    // Look for [STATUS: ...] or # STATUS: ... or > **Document Status:** ...
    const statusMatch = content.match(/\[STATUS:\s*([^\]]+)\]/i) || content.match(/#\s*STATUS:\s*([^\r\n]+)/i) || content.match(/> \*\*Document Status:\*\*\s*([^\r\n]+)/i);
    if (statusMatch && !status.includes('OUT OF CORE SCOPE')) {
        status = statusMatch[1].trim();
    }

    return {
        name: fileName,
        path: filePath.replace(ROOT, '').replace(/\\/g, '/'),
        status: status,
        type: fileName.endsWith('.md') ? 'documentation' : 'code',
        track: track
    };
}

function generateAiIndex(targetDir) {
    console.log('[SYNC] Generating AI Index...');
    const index = [];
    const sourceDirs = [
        path.join(targetDir, 'whitepapers'),
        path.join(targetDir, 'whitepapers-legacy'),
        path.join(targetDir, 'hypotheses'),
        path.join(targetDir, 'core'),
        path.join(targetDir, 'project'),
        path.join(targetDir, 'workflows'),
        path.join(targetDir, 'portal-structure'), // Added portal structure
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
            } else if (['.md', '.js', '.ts', '.svelte', '.py', '.json'].some(ext => item.endsWith(ext))) {
                // Skip ai_index.json itself to avoid recursion/bloat
                if (item === 'ai_index.json') continue;

                const content = fs.readFileSync(fullPath, 'utf8');
                // Basic security: skip if it looks like it contains keys (very crude check)
                if (content.includes('AIzaSy')) continue;

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

    // 1. Sync directories
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

    // 2. Sync individual files (Core & Project)
    const allFilesToSync = [...coreFilesToSync, ...projectFilesToSync];
    for (const { source, target } of allFilesToSync) {
        const sourcePath = path.join(ROOT, source);
        const targetPath = path.join(path.resolve(__dirname, '../'), target);

        if (fs.existsSync(sourcePath)) {
            console.log(`[SYNC] Syncing file: ${source} -> ${targetPath}`);
            copyRecursiveSync(sourcePath, targetPath);
        } else {
            console.warn(`[SYNC] Warning: Source file not found: ${sourcePath}`);
        }
    }

    // 3. Smart Audit Sync
    try {
        const latestRunPath = path.join(ROOT, 'output_wp/latest_run.txt');
        if (fs.existsSync(latestRunPath)) {
            const latestRunRel = fs.readFileSync(latestRunPath, 'utf8').trim();
            const auditReportPath = path.join(ROOT, 'output_wp', latestRunRel, 'audit_report.json'); // Assuming this structure

            // Note: If audit_report.json doesn't exist, we might want to check for something else or just skip
            if (fs.existsSync(auditReportPath)) {
                const targetPath = path.join(DATA_TARGET, 'project/audit_latest.json');
                console.log(`[SYNC] Syncing latest audit report: ${auditReportPath} -> ${targetPath}`);
                copyRecursiveSync(auditReportPath, targetPath);
            } else {
                console.warn(`[SYNC] Latest audit run found (${latestRunRel}), but 'audit_report.json' is missing.`);
            }
        }
    } catch (e) {
        console.warn('[SYNC] Failed to sync audit report:', e.message);
    }

    // Generate AI Index
    generateAiIndex(DATA_TARGET);

    console.log('[SYNC] Synchronization complete.');
}

// Export for testing
export { sync, findRoot };

// Run if called directly
import { pathToFileURL } from 'url';
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
    try {
        sync();
    } catch (err) {
        console.error('[SYNC] Critical error during synchronization:', err);
        process.exit(1);
    }
}
