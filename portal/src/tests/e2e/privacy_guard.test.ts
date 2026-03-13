
import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// Configuration: Whileged storage keys and locations
// Format: "filename": ["allowed_key_1", "allowed_key_2"]
const STORAGE_WHITELIST: Record<string, string[]> = {
    'CookieBanner.svelte': ['cookie_consent'],
    'ResonanceDeck.svelte': ['resonance_history', 'cookie_consent', 'lina_session_id'], // cookie_consent is read here too
    'AiResearch.svelte': ['lineum_research_history'],
    'privacy.test.ts': ['cookie_consent'],
    'chat_flow.test.ts': ['resonance_history'], // Simulates chat history
    'wiki_warning.spec.ts': ['lineum_whitepaper_warning_acknowledged', 'wiki_warning_ack'],
    'api_solutions_interactions.spec.ts': ['cookie_consent'],
    'WikiWarning.svelte': ['wiki_warning_ack'],
    'setup.ts': [],
    '+page.svelte': ['lineum_whitepaper_warning_acknowledged'],
    'privacy_guard.test.ts': ['cookie_consent', 'resonance_history', 'lineum_research_history', 'key'], // The guard itself reads these for regex matching context or verification
    'mobile.spec.ts': ['cookie_consent'],
};

// Regex to find storage usage
// Matches: localStorage.getItem('key'), localStorage.setItem("key"), etc.
// Also simple matches for 'cookie' to catch document.cookie
const STORAGE_REGEX = /(?:localStorage|sessionStorage)\.(?:getItem|setItem|removeItem)\s*\(\s*['"]([^'"]+)['"]|document\.cookie/g;

function scanDirectory(dir: string, fileList: string[] = []) {
    const files = fs.readdirSync(dir);

    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);

        if (stat.isDirectory()) {
            if (file !== 'node_modules' && file !== '.svelte-kit' && file !== '.git') {
                scanDirectory(filePath, fileList);
            }
        } else {
            if (file.endsWith('.svelte') || file.endsWith('.ts') || file.endsWith('.js')) {
                fileList.push(filePath);
            }
        }
    });

    return fileList;
}

test.describe('Privacy Guard', () => {
    test('Source code should not contain undocumented storage usage', async () => {
        // Use process.cwd() which is usually the project root (where package.json and playwright.config.ts are)
        const srcDir = path.join(process.cwd(), 'src');
        console.log(`Scanning directory: ${srcDir}`);

        const files = scanDirectory(srcDir);
        console.log(`Found ${files.length} files to scan.`);

        const violations: string[] = [];

        files.forEach(filePath => {
            const content = fs.readFileSync(filePath, 'utf-8');
            const fileName = path.basename(filePath);

            let match;
            while ((match = STORAGE_REGEX.exec(content)) !== null) {
                const fullMatch = match[0];
                const key = match[1]; // The captured key name, if present

                // 1. Check if file is in whitelist
                const allowedKeys = STORAGE_WHITELIST[fileName];

                if (!allowedKeys) {
                    // File not in whitelist at all
                    violations.push(`File ${fileName} uses storage but is not whitelisted: ${fullMatch}`);
                    continue;
                }

                // 2. Check if key is allowed (if we extracted a key)
                if (key) {
                    if (!allowedKeys.includes(key)) {
                        violations.push(`File ${fileName} uses unapproved key '${key}': ${fullMatch}`);
                    }
                } else {
                    // Match was something general like document.cookie or variable access
                    // For now, if the file is whitelisted, we assume manual review passed.
                    // But if it's document.cookie, we might want to be stricter.
                    if (fullMatch.includes('document.cookie')) {
                        // strict check for document.cookie?
                    }
                }
            }
        });

        if (violations.length > 0) {
            console.log("--- PRIVACY VIOLATIONS FOUND ---");
            violations.forEach(v => console.log(v));
            console.log("--------------------------------");
            console.log("ACTION REQUIRED: You have introduced new storage usage (localStorage/cookies).");
            console.log("1. Verify if this storage usage is compliant with GDPR.");
            console.log("2. Update 'src/routes/privacy/+page.svelte' to disclose this usage.");
            console.log("3. Add the key to STORAGE_WHITELIST in this test file to approve it.");
            fs.writeFileSync(path.join(process.cwd(), 'violations.json'), JSON.stringify(violations, null, 2));
        }

        expect(violations, `Found ${violations.length} privacy violations. See console for details. You MUST update the Privacy Policy before whitelisting new keys.`).toEqual([]);
    });
});
