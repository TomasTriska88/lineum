import { describe, it, expect } from 'vitest';
import { readdirSync, statSync } from 'fs';
import { join, extname } from 'path';

describe('Repository Hygiene Enforcement', () => {
    it('ensures no temporary scrape/log files are left in the root or portal directories', () => {
        // Paths to check
        const projectRoot = join(process.cwd(), '../');
        const portalRoot = process.cwd();

        const dirsToCheck = [
            { name: 'Project Root', path: projectRoot },
            { name: 'Portal Root', path: portalRoot }
        ];

        // Forbidden exact extensions (nobody should have a raw .log or .tmp checked into root)
        const forbiddenExts = ['.log', '.tmp', '.zip'];

        // Allowed generic JSON files in roots
        const allowedJsons = ['package.json', 'package-lock.json', 'tsconfig.json', 'svelte.config.js', 'lineum-config.json', 'audit_info_thermodynamics.json', 'audit_stencil_ablation.json', 'lang_test_results.json', 'rigor_mode_coupling.json', 'output_audit_saturation.json', 'railway.json', '.zenodo.json'];

        // Allowed TXT files in roots 
        const allowedTxt = ['requirements.txt', 'requirements-dev.txt', 'audit_log.txt', 'broca_results.txt', 'clean_audit.txt', 'github_rules.txt', 'icon-interpretation.txt', 'pr_rules.txt', 'public_rules.txt', 'smetak_oea_rules.txt', 'timing_audit.txt', 'robots.txt'];

        // Allowed PY files in root
        const allowedPy = ['lineum.py'];

        // Forbidden prefixes for .txt or .json (common AI scratch patterns)
        const tempPrefixes = ['test_output', 'error_log', 'ci_failure', 'diag_out', 'prompt_out', 'lang_out', 'verify_out', 'repro_', 'console_', 'final_', 'alias_', 'check_out', 'playwright_out', 'test-', 'results', 'violations', 'output_', 'test_'];

        const violations: string[] = [];

        for (const dir of dirsToCheck) {
            try {
                const files = readdirSync(dir.path);
                for (const file of files) {
                    const fullPath = join(dir.path, file);
                    const isFile = statSync(fullPath).isFile();

                    if (isFile) {
                        const ext = extname(file).toLowerCase();
                        const lowerFile = file.toLowerCase();

                        if (forbiddenExts.includes(ext)) {
                            violations.push(`[${dir.name}] Forbidden extension: ${file}`);
                        } else if (ext === '.json') {
                            if (!allowedJsons.includes(lowerFile)) {
                                violations.push(`[${dir.name}] Unrecognized JSON in root: ${file}`);
                            }
                        } else if (ext === '.txt') {
                            if (!allowedTxt.includes(lowerFile)) {
                                violations.push(`[${dir.name}] Unrecognized TXT in root: ${file}`);
                            }
                        } else if (ext === '.py' && dir.name === 'Project Root') {
                            if (!allowedPy.includes(lowerFile)) {
                                violations.push(`[${dir.name}] Unrecognized Python file in root: ${file}`);
                            }
                        }

                        // Additionally check against prefix list for extra safety on allowed extensions
                        for (const prefix of tempPrefixes) {
                            if (lowerFile.startsWith(prefix) && lowerFile !== 'pytest.ini' && !allowedJsons.includes(lowerFile) && !allowedTxt.includes(lowerFile)) {
                                violations.push(`[${dir.name}] Suspected temp file by prefix: ${file}`);
                                break;
                            }
                        }
                    }
                }
            } catch (e) {
                console.error(`Failed to scan ${dir.name}:`, e);
            }
        }

        if (violations.length > 0) {
            console.error('\n🚨 REPOSITORY HYGIENE VIOLATIONS DETECTED 🚨');
            console.error('The following files violate the /scratch workflow rules. They MUST be moved to the .scratch/ directory or deleted.');
            violations.forEach(v => console.error(' - ' + v));
        }

        expect(violations.length, `Found ${violations.length} temporary files in root directories. They belong in .scratch/`).toBe(0);
    });
});
