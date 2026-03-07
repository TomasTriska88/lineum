import path from 'path';
import { checkFile, walkDir } from '../../helpers/check-czech-lib.js';

import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SRC_DIR = path.join(__dirname, '../src');

console.log('Checking for Czech characters in Portal src directory...');
let hasErrors = false;

walkDir(SRC_DIR, (filePath) => {
    // Skip binary files and specific extensions if needed
    // Skip auto-generated paraglide messages which naturally contain translations
    if (filePath.includes('paraglide') || filePath.includes('paraglide\\messages') || filePath.includes('paraglide/messages')) {
        return;
    }

    // Skip tests
    const normalizedPath = filePath.replace(/\\/g, '/');
    if (normalizedPath.includes('/test/') || normalizedPath.includes('/tests/')) {
        return;
    }

    // Skip content/lore data where Czech references are allowed
    if (normalizedPath.includes('/src/lib/data/') || normalizedPath.includes('/about/') || normalizedPath.includes('/api-showcase/')) {
        return;
    }

    // Skip utility files that legitimately contain character matching logic
    if (normalizedPath.includes('/utils/tts_utils') || normalizedPath.includes('/utils/chatUtils')) {
        return;
    }

    if (path.extname(filePath).match(/\.(svelte|ts|js|css|html)$/)) {
        if (checkFile(filePath)) {
            hasErrors = true;
        }
    }
});

if (hasErrors) {
    const warnMode = process.argv.includes('--warn');
    if (warnMode) {
        console.warn('\nWARNING: Czech characters detected! (Non-blocking mode)');
        console.warn('Please eventually migrate to English in the portal.');
        process.exit(0);
    } else {
        console.error('\nFAIL: Czech characters detected! Please use only English in the portal.');
        process.exit(1);
    }
} else {
    console.log('\nPASS: No Czech characters found in the Portal.');
    process.exit(0);
}
