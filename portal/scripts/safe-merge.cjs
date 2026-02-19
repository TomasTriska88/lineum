const { execSync } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// ANSI colors for output
const colors = {
    reset: "\x1b[0m",
    green: "\x1b[32m",
    red: "\x1b[31m",
    yellow: "\x1b[33m",
    cyan: "\x1b[36m"
};

function log(message, color = colors.reset) {
    console.log(`${color}[Safe-Merge] ${message}${colors.reset}`);
}

function error(message) {
    console.error(`${colors.red}[Safe-Merge] ERROR: ${message}${colors.reset}`);
    process.exit(1);
}

function run(command, description) {
    const isDryRun = process.argv.includes('--dry-run');
    try {
        log(`Running: ${description}...`, colors.cyan);
        if (isDryRun && command.startsWith('git push')) {
            log(`[DRY-RUN] Would execute: ${command}`, colors.yellow);
            return;
        }
        execSync(command, { stdio: 'inherit' });
        log(`✓ ${description} complete.`, colors.green);
    } catch (e) {
        error(`Failed to ${description}. Command: ${command}`);
    }
}

function checkClean() {
    try {
        const status = execSync('git status --porcelain', { encoding: 'utf-8' });
        if (status.length > 0) {
            log("Dirty files:", colors.red);
            console.log(status);
            error("Working directory is not clean. Please commit or stash changes before merging.");
        }
    } catch (e) {
        error("Failed to check git status.");
    }
}

async function askConfirmation() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise(resolve => {
        rl.question(`${colors.yellow}About to push to main. Are you sure? (y/N): ${colors.reset}`, answer => {
            rl.close();
            resolve(answer.toLowerCase() === 'y');
        });
    });
}

async function main() {
    log("Starting Safe Merge Workflow...");

    // Clean .test-output
    const testOutputDir = path.join(__dirname, '../.test-output');
    if (fs.existsSync(testOutputDir)) {
        log("Cleaning .test-output...", colors.cyan);
        try {
            fs.rmSync(testOutputDir, { recursive: true, force: true });
        } catch (e) {
            log("Warning: Failed to clean .test-output (might be open). Continuing.", colors.yellow);
        }
    }

    // 1. Check for clean working directory
    checkClean();

    // 2. Checkout main and pull latest
    // Use force checkout to discard local changes in tracked files immediately
    run('git checkout -f main', 'Switch to main branch (forced)');
    run('git pull origin main', 'Pull latest main');

    // GUARD: Reset any ghost changes from auto-sync triggers (e.g. VS Code or running dev server)
    try {
        log("Forcing git reset --hard HEAD to clean generated files...", colors.yellow);
        execSync('git reset --hard HEAD', { stdio: 'inherit' });
    } catch (e) {
        log("Warning: Reset failed.", colors.red);
    }

    // 3. Merge dev
    try {
        log("Merging dev into main...", colors.cyan);
        execSync('git merge dev', { stdio: 'inherit' });
    } catch (e) {
        error("Merge failed. Please resolve conflicts manually and try again.");
    }

    // 4. SYNC DATA (This is critical for Lina's context)
    run('npm run sync', 'Synchronize Data & Context');

    // 5. Run Tests
    log("Running Validation Tests...", colors.yellow);
    try {
        run('npm test', 'Unit Tests & System Verification');
        run('npm run test:e2e', 'E2E Tests');
    } catch (e) {
        log("Tests Failed! rolling back...", colors.red);
        // Robust rollback: Reset to origin/main (since we pulled it) then checkout dev
        execSync('git reset --hard origin/main');
        execSync('git checkout dev');
        error("Tests failed. Merge aborted and changes rolled back.");
    }

    // 6. Confirmation and Push
    log("All tests passed! Data is synced.", colors.green);

    let confirmed = false;
    if (process.argv.includes('--yes') || process.argv.includes('-y')) {
        confirmed = true;
    } else {
        confirmed = await askConfirmation();
    }

    if (confirmed) {
        run('git push origin main', 'Push to Main');
        run('git checkout dev', 'Switch back to dev');
        log("Merge Successful! Application updated.", colors.green);
    } else {
        log("Push cancelled by user. Rolling back merge...", colors.yellow);
        execSync('git reset --hard HEAD~1');
        execSync('git checkout dev');
        log("Rollback complete.", colors.green);
    }
}

main();
