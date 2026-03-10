import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const portalSrcDir = path.resolve(__dirname, '../src');
const portalRootDir = path.resolve(__dirname, '../');
const labSrcDir = path.resolve(__dirname, '../../lab/src');
const labRootDir = path.resolve(__dirname, '../../lab');

const dirsToScan = [portalSrcDir, labSrcDir];
const filesToScanRoot = [portalRootDir, labRootDir];
function scanDirectory(directory) {
    // Ignore static data structure archiver dumps
    if (directory.includes(path.join('src', 'lib', 'data')) || directory.includes(path.join('src', 'tests', 'data'))) {
        return false;
    }

    let hasError = false;
    const files = fs.readdirSync(directory);

    for (const file of files) {
        const fullPath = path.join(directory, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
            hasError = scanDirectory(fullPath) || hasError;
        } else if (file.endsWith('.ts') || file.endsWith('.js') || file.endsWith('.svelte') || file.startsWith('.env')) {
            const content = fs.readFileSync(fullPath, 'utf-8');
            // We ignore base.ts because it configures playwright itself, allowing localhost for data URIs
            if (file !== 'base.ts' && content.toLowerCase().includes('localhost')) {
                console.error(`\x1b[31m[ERROR] Found 'localhost' in ${fullPath}\x1b[0m`);
                console.error(`\x1b[33mAll frontend fetches and E2E specs must use '127.0.0.1' due to IPv6 routing bugs in modern Node APIs. Please refactor this file.\x1b[0m\n`);
                hasError = true;
            }
        }
    }

    return hasError;
}

console.log("Checking frontend source and tests for 'localhost' references...");
let failed = false;
for (const d of dirsToScan) {
    if (fs.existsSync(d)) {
        failed = scanDirectory(d) || failed;
    }
}

// Manually check .env files in root dirs
function scanRootFiles(directory) {
    let hasError = false;
    if (!fs.existsSync(directory)) return false;
    const files = fs.readdirSync(directory);
    for (const file of files) {
        if (file.startsWith('.env')) {
            const fullPath = path.join(directory, file);
            const content = fs.readFileSync(fullPath, 'utf-8');
            if (content.toLowerCase().includes('localhost')) {
                console.error(`\x1b[31m[ERROR] Found 'localhost' in ${fullPath}\x1b[0m`);
                hasError = true;
            }
        }
    }
    return hasError;
}

for (const d of filesToScanRoot) {
    failed = scanRootFiles(d) || failed;
}

if (failed) {
    process.exit(1);
} else {
    console.log("\x1b[32m[OK] No 'localhost' references found.\x1b[0m");
    process.exit(0);
}
