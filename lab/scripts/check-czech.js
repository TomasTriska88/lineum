import path from 'path';
import { checkFile, walkDir } from '../../helpers/check-czech-lib.js';

const SRC_DIR = 'src';

console.log('Checking for Czech characters in Lab src directory...');
let hasErrors = false;

walkDir(SRC_DIR, (filePath) => {
    if (path.extname(filePath).match(/\.(svelte|ts|js|css|html)$/)) {
        if (checkFile(filePath)) {
            hasErrors = true;
        }
    }
});

if (hasErrors) {
    console.error('\nFAIL: Czech characters detected! Please use only English in the Laboratory.');
    process.exit(1);
} else {
    console.log('\nPASS: No Czech characters found in the Laboratory.');
    process.exit(0);
}
