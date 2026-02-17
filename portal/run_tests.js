const { execSync } = require('child_process');
const fs = require('fs');

try {
    const output = execSync('npx vitest run src/test/chat_flow.test.ts', { encoding: 'utf8' });
    fs.writeFileSync('test_run.log', output);
    console.log('Tests passed or finished.');
} catch (error) {
    fs.writeFileSync('test_run.log', error.stdout || error.message);
    console.log('Tests failed, log captured.');
}
