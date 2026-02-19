
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PORTAL_ROOT = path.resolve(__dirname, '../');
const PROJECT_ROOT = path.resolve(PORTAL_ROOT, '../');
const ASSETS_DEST = path.join(PORTAL_ROOT, 'railway_assets');

// Define what needs to be copied for Railway Restricted Context
const ASSETS_TO_MIRROR = [
    { source: 'whitepapers', type: 'dir' },
    { source: 'hypotheses', type: 'dir' },
    { source: 'whitepaper-old', type: 'dir' },
    { source: 'source', type: 'dir' },
    { source: 'lineum.py', type: 'file' },
    { source: 'tools', type: 'dir' },
    { source: 'README.md', type: 'file', new_name: 'README_PROJECT.md' },
    { source: 'LICENSE', type: 'file' },
    { source: 'todo.md', type: 'file' },
    { source: 'CITATION.cff', type: 'file' },
    { source: '.zenodo.json', type: 'file' },
    { source: 'railway.json', type: 'file' },
    { source: 'requirements.txt', type: 'file' }
];

function copyRecursiveSync(src, dest) {
    if (!fs.existsSync(src)) {
        console.warn(`[STAGE] Source not found: ${src}`);
        return;
    }
    const stats = fs.statSync(src);
    if (stats.isDirectory()) {
        if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
        fs.readdirSync(src).forEach(child => {
            copyRecursiveSync(path.join(src, child), path.join(dest, child));
        });
    } else {
        const destDir = path.dirname(dest);
        if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });
        fs.copyFileSync(src, dest);
    }
}

console.log('[STAGE] Starting Railway Asset Staging...');
console.log(`[STAGE] Project Root: ${PROJECT_ROOT}`);
console.log(`[STAGE] Assets Dest: ${ASSETS_DEST}`);

// Clean previous run
if (fs.existsSync(ASSETS_DEST)) {
    console.log('[STAGE] Cleaning previous assets...');
    fs.rmSync(ASSETS_DEST, { recursive: true, force: true });
}
fs.mkdirSync(ASSETS_DEST, { recursive: true });

ASSETS_TO_MIRROR.forEach((item) => {
    const srcPath = path.join(PROJECT_ROOT, item.source);
    // Use new_name if provided, otherwise keep basename
    const destName = item.new_name || path.basename(item.source);
    const destPath = path.join(ASSETS_DEST, destName);

    console.log(`[STAGE] Mirroring ${item.source} -> ${destPath}`);
    copyRecursiveSync(srcPath, destPath);
});

console.log('[STAGE] Staging Complete. Assets are in portal/railway_assets/');
console.log('[STAGE] Please commit this folder before pushing to Railway.');
