import path from 'path';
import { checkFile, walkDir } from '../helpers/check-czech-lib.js';

import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SRC_DIR = path.join(__dirname, '../tests');

console.log('Checking for Czech characters in tests directory...');
let hasErrors = false;

walkDir(SRC_DIR, (filePath) => {
    // Skip tests that purposefully test Czech characters or contain allowed Czech strings for assertions
    const normalizedPath = filePath.replace(/\\/g, '/');
    const allowedTests = [
        'test_whitepaper_language_policy.py',
        'test_todo_language_policy.py',
        'test_scripts_language_policy.py',
        'test_repro_scripts.py',
        'test_performance.py',
        'test_lineum_knobs.py',
        'check-czech-lib.test.js'
    ];

    if (allowedTests.some(allowed => normalizedPath.includes(allowed))) {
        return;
    }

    // We only check python, javascript, markdown, or other test files.
    if (path.extname(filePath).match(/\.(py|js|ts|spec\.js|md|json)$/)) {
        if (checkFile(filePath)) {
            hasErrors = true;
        }
    }
});

if (hasErrors) {
    console.error('\nFAIL: Czech characters detected! Please use only English in the tests.');
    process.exit(1);
} else {
    console.log('\nPASS: No Czech characters found in the tests.');
    process.exit(0);
}
