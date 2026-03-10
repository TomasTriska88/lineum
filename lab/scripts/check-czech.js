import path from 'path';
import { checkFile, walkDir } from '../../helpers/check-czech-lib.js';

import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SRC_DIR = path.join(__dirname, '../src');
const DOC_FILE = path.join(__dirname, '../../portal/LAB_UX_CANON.md');

console.log('Checking for Czech characters in Lab src and documentation...');
let hasErrors = false;

walkDir(SRC_DIR, (filePath) => {
    if (path.extname(filePath).match(/\.(svelte|ts|js|css|html|json)$/)) {
        if (checkFile(filePath)) {
            hasErrors = true;
        }
    }
});

// Also check the UX Canon documentation specifically
if (checkFile(DOC_FILE)) {
    hasErrors = true;
}

if (hasErrors) {
    console.error('\nFAIL: Czech characters detected! Please use only English in the Laboratory and Documentation.');
    process.exit(1);
} else {
    console.log('\nPASS: No Czech characters found in the Laboratory and Documentation.');
    process.exit(0);
}
