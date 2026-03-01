const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const scratchDir = path.join(__dirname, '.scratch');

if (!fs.existsSync(scratchDir)) {
    fs.mkdirSync(scratchDir, { recursive: true });
}

try {
    const output = execSync('npx vitest run src/tests/chat_flow.test.ts', { encoding: 'utf8' });
    fs.writeFileSync(path.join(scratchDir, 'test_run.log'), output);
    console.log('Tests passed or finished.');
} catch (error) {
    fs.writeFileSync(path.join(scratchDir, 'test_run.log'), error.stdout || error.message);
    console.log('Tests failed, log captured.');
}
