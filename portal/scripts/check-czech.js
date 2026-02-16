import fs from 'fs';
import path from 'path';

const SRC_DIR = 'src';
const CZECH_CHARS = /[áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]/;

function checkFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    let found = false;

    lines.forEach((line, index) => {
        if (CZECH_CHARS.test(line)) {
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
    if (path.extname(filePath).match(/\.(svelte|ts|js|css|html)$/)) {
        if (checkFile(filePath)) {
            hasErrors = true;
        }
    }
});

if (hasErrors) {
    console.error('\nFAIL: Czech characters detected! Please use only English in the portal.');
    process.exit(1);
} else {
    console.log('\nPASS: No Czech characters found.');
    process.exit(0);
}
