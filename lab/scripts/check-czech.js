import path from 'path';
import { checkFile, walkDir } from '../../helpers/check-czech-lib.js';

const SRC_DIR = 'src';
const DOC_FILE = '../portal/LAB_UX_CANON.md';

console.log('Checking for Czech characters in Lab src and documentation...');
let hasErrors = false;

walkDir(SRC_DIR, (filePath) => {
    // Ignore translation dictionary files which naturally contain Czech
    if (filePath.includes('i18n.js') || filePath.includes('i18n.test.js') || filePath.includes('translations')) return;

    if (path.extname(filePath).match(/\.(svelte|ts|js|css|html)$/)) {
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
