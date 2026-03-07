import { execSync } from 'child_process';
import path from 'path';

console.log('--- Running Global Czech Character Checks ---');

const scripts = [
    { name: 'Tests', cmd: 'node scripts/check-czech-tests.js', cwd: path.join(process.cwd()) },
    { name: 'Lab', cmd: 'node lab/scripts/check-czech.js', cwd: path.join(process.cwd()) },
    { name: 'Portal', cmd: 'node portal/scripts/check-czech.js', cwd: path.join(process.cwd()) }
];

let globalFail = false;

for (const script of scripts) {
    console.log(`\n>>> Checking ${script.name}...`);
    try {
        execSync(script.cmd, { stdio: 'inherit', cwd: script.cwd });
    } catch (err) {
        console.error(`\n[!] ${script.name} check failed.`);
        if (err.stdout) console.log(err.stdout);
        if (err.stderr) console.error(err.stderr);
        globalFail = true;
    }
}

if (globalFail) {
    console.error('\n❌ GLOBAL CHECK FAILED: Czech characters detected where they should not be.');
    process.exit(1);
} else {
    console.log('\n✅ GLOBAL CHECK PASSED: No forbidden Czech characters found.');
    process.exit(0);
}
