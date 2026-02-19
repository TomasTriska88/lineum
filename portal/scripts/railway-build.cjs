const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ANSI colors
const colors = {
    reset: "\x1b[0m",
    green: "\x1b[32m",
    red: "\x1b[31m",
    yellow: "\x1b[33m",
    cyan: "\x1b[36m"
};

function log(message, color = colors.reset) {
    console.log(`${color}[Railway-Build] ${message}${colors.reset}`);
}

function run(command) {
    log(`Running: ${command}`, colors.cyan);
    execSync(command, { stdio: 'inherit' });
}

function main() {
    const branch = process.env.RAILWAY_GIT_BRANCH || process.env.HEAD || 'unknown';
    log(`Detected Branch: ${branch}`, colors.yellow);

    if (branch === 'main') {
        log("MAIN BRANCH DETECTED - PROCEEDING WITH PRODUCTION GATES", colors.green);

        try {
            // 1. Sync Data
            run('npm run sync');

            // 2. Run Tests (Strict Gate)
            log("Running Unit Tests...", colors.cyan);
            // We skip E2E on Railway to avoid browser overhead/flakiness unless configured
            run('npm test');

            // 3. Build
            log("Building Production App...", colors.cyan);
            run('vite build');

            log("✅ Build Complete for Main.", colors.green);
        } catch (e) {
            log("❌ Deployment Failed during Gates/Build.", colors.red);
            process.exit(1);
        }
    } else {
        log("DEV/OTHER BRANCH DETECTED - PARKING DEPLOYMENT", colors.yellow);
        log("User requested no dev builds on Railway. Creating idle artifact to prevent crash loops.", colors.reset);

        // Create a dummy build directory and script to prevent 'node build' from crashing on start
        const buildDir = path.join(__dirname, '../build');
        if (!fs.existsSync(buildDir)) {
            fs.mkdirSync(buildDir, { recursive: true });
        }

        const dummyServer = `
            console.log("------------------------------------------------");
            console.log("   LINEUM PORTAL - DEV MODE PARKED              ");
            console.log("   (Deployment skipped as requested)            ");
            console.log("------------------------------------------------");
            // Idling to prevent container restart loop
            setInterval(() => {}, 1000 * 60 * 60); 
        `;

        fs.writeFileSync(path.join(buildDir, 'index.js'), dummyServer);
        fs.writeFileSync(path.join(buildDir, 'handler.js'), dummyServer); // SvelteKit adapter-node often outputs handler.js or index.js depending on config, covering bases.
        log("✅ Parking logic applied. Exiting success.", colors.green);
        process.exit(0);
    }
}

main();
