const { execSync } = require('child_process');
try {
    const out = execSync('npx playwright test tests/app.spec.js -g "Fullscreen mode containers do not overlap" --project="Mobile Chrome"', { encoding: 'utf-8' });
    console.log(out);
} catch (e) {
    console.log(e.stdout);
    console.log(e.stderr);
}
