import fs from 'fs';
import path from 'path';

const SRC_DIR = 'src';
const CZECH_CHARS = /[áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]/;

function checkFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    let found = false;

    lines.forEach((line, index) => {
        // Safe words whitelist
        let sanitizedLine = line.replace(/Čeština/g, '');

        if (CZECH_CHARS.test(sanitizedLine)) {
            console.error(`Czech character found in ${filePath}:${index + 1}:`);
            console.error(`  > ${line.trim()}`);
            found = true;
        }
    });

    return found;
}

function walkDir(dir, callback) {
    fs.readdirSync(dir).forEach(f => {
        const dirPath = path.join(dir, f);
        const isDirectory = fs.statSync(dirPath).isDirectory();
        isDirectory ? walkDir(dirPath, callback) : callback(dirPath);
    });
}

console.log('Checking for Czech characters in src directory...');
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
    if (filePath.includes(path.join('src', 'lib', 'data')) || filePath.includes('about')) {
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
    console.log('\nPASS: No Czech characters found.');
    process.exit(0);
}
