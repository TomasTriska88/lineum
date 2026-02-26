import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

// Tento test provadi heuristickou a statistickou kontrolu lingvisticke kvality
// BEZ nutnosti volat jakakoliv externi LLM API (jako je Gemini, OpenAI).
// Ridi se sadou pravidel vytvorenych pro odhaleni zjevnych nezadoucih strojovych prekladu.

describe('Heuristic Linguistic Quality Assurance', () => {
    const langs = ['cs', 'de', 'ja'];
    const messagesPath = path.resolve(__dirname, '../../messages');

    const dicts: Record<string, Record<string, string>> = {};
    for (const lang of ['en', ...langs]) {
        const fileContent = fs.readFileSync(path.join(messagesPath, `${lang}.json`), 'utf-8');
        dicts[lang] = JSON.parse(fileContent);
    }

    // Detekce tupych doslovnych prekladu a anglicismu
    const commonMachineTranslationErrors: Record<string, string[]> = {
        'cs': [
            'odeslat dotaz',     // Cizi 'Submit Query' misto prirozenejsich tlacitek
            'aplikace je běžící',// Hruby preklad misto 'Aplikace bezi'
            'tvrdý kód',         // 'hardcode' strojove
            'vítejte u',         // Hruby preklad 'welcome to'
            'zavázat se',        // Spatny preklad 'Commit' u Gitu
            '[insert',
            'translate this',
            '[todo]'
        ],
        'de': [
            'es macht sinn',     // Anglicismus 'it makes sense', spravne je 'es ergibt Sinn'
            'in 2024',           // Anglicismus, v nemcine je to jen '2024' nebo 'im Jahr 2024'
            'für sicher',        // 'for sure', spravne 'sicherlich'
            '[insert',
            'translate this',
            '[todo]'
        ],
        'ja': [
            'あなたは',           // Naduzivani zajmen 'anata wa' (you) je typickym znakem spatneho prekladu
            'クリックここ',       // 'Click here' doslovne (kurikku koko), misto spravneho 'kochira o kurikku'
            '[insert',
            'translate this',
            '[todo]'
        ]
    };

    it('should pass heuristics for unnatural or aggressive machine translation markers', () => {
        // Kontrola tupych prekladu na zaklade nasich markeru
        for (const lang of langs) {
            const markers = commonMachineTranslationErrors[lang];
            const data = Object.values(dicts[lang]);

            for (const text of data) {
                if (typeof text !== 'string') continue;

                const lower = text.toLowerCase();
                for (const marker of markers) {
                    expect(lower, `Found highly probable unnatural machine translation in [${lang}]: '${text}' contained '${marker}'`).not.toContain(marker.toLowerCase());
                }
            }
        }
    });

    it('should flag inappropriately formal or literal strings (Length Expansion Ratio Test)', () => {
        // Tupé strojové překlady se často vyznačují neschopností udržet konciznost angličtiny.
        // Není přirozené, aby se z tlačítka 'Save' vyklubala 5 slovná obří věta.

        const baseKeys = Object.keys(dicts['en']);

        for (const lang of langs) {
            let suspiciousExpansions = 0;

            for (const key of baseKeys) {
                const enText = dicts['en'][key];
                const targetText = dicts[lang][key];

                if (!enText || !targetText) continue;

                // Zajimaji nas zejm. UI prvky (kratke stringy pod 20 znaku)
                if (enText.length > 3 && enText.length < 20) {
                    const ratio = targetText.length / enText.length;

                    // Pokud je jazyk vice jak 3x delsi, povazujeme to za podezrele nafouknuti
                    if (ratio > 3.0 && targetText.length > 20) {
                        suspiciousExpansions++;
                    }
                }
            }

            // Ocekavame, ze dobry projekt by mel tyto abnormality peclive ladit
            expect(suspiciousExpansions, `Too many suspicious string length expansions in ${lang}`).toBeLessThan(5);
        }
    });

    it('should statically forbid splitting Paraglide strings via gradient spans', () => {
        // Prevents incorrect splitting like: {m.foo()} <span class="text-gradient-multi">{m.bar()}</span>
        // This is forbidden because it destroys the ability to reorder words for different languages (e.g., Japanese vs German).

        const srcDir = path.resolve(__dirname, '../../src');

        function findSvelteFiles(dir: string, fileList: string[] = []) {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const stat = fs.statSync(path.join(dir, file));
                if (stat.isDirectory()) {
                    findSvelteFiles(path.join(dir, file), fileList);
                } else if (file.endsWith('.svelte')) {
                    fileList.push(path.join(dir, file));
                }
            }
            return fileList;
        }

        const svelteFiles = findSvelteFiles(srcDir);
        let offenders: string[] = [];

        // Look for pattern: {m.something()} and closely followed by <span class="text-gradient-multi">{m.another_thing()}</span>
        // Although regex isn't a perfect AST parser, it effectively catches instances of two paraglide keys separated by a static span.
        const forbiddenPattern = /\{m\.[a-zA-Z0-9_]+\(\)\}[\s\S]{0,150}<span[^>]*class=["'][^"']*text-gradient-multi[^"']*["'][^>]*>[\s\S]{0,150}\{m\.[a-zA-Z0-9_]+\(\)\}/;

        for (const sf of svelteFiles) {
            const content = fs.readFileSync(sf, 'utf-8');
            if (forbiddenPattern.test(content)) {
                offenders.push(path.basename(sf));
            }
        }

        // The test must pass cleanly; no files should contain this split pattern
        expect(offenders.length, `Found incorrectly split translated strings using gradient spans in: ${offenders.join(', ')}. Use parameterized strings instead!`).toBe(0);
    });

    it('should forbid data-sveltekit-reload on hash links to preserve Paraglide reactivity', () => {
        // Prevents the usage of the data-sveltekit-reload attribute on links starting with a hash (e.g., href="/#scientist" or href="#faq").
        // This ensures SPA navigation and Paraglide translations do not lose reactivity by forcing a hard page reload from the server.

        const srcDir = path.resolve(__dirname, '../../src');

        function findSvelteFiles(dir: string, fileList: string[] = []) {
            const files = fs.readdirSync(dir);
            for (const file of files) {
                const stat = fs.statSync(path.join(dir, file));
                if (stat.isDirectory()) {
                    findSvelteFiles(path.join(dir, file), fileList);
                } else if (file.endsWith('.svelte')) {
                    fileList.push(path.join(dir, file));
                }
            }
            return fileList;
        }

        const svelteFiles = findSvelteFiles(srcDir);
        let offenders: string[] = [];

        // Looking for: <a ... href="[anything]#something" ... data-sveltekit-reload ... > 
        // or in reverse order: <a ... data-sveltekit-reload ... href="[anything]#something" ... >
        const badHashLinkPattern = /<a[^>]+(?:href=["'][^"']*#[^"']*["'][^>]*data-sveltekit-reload|data-sveltekit-reload[^>]*href=["'][^"']*#[^"']*["'])[^>]*>/i;

        for (const sf of svelteFiles) {
            const content = fs.readFileSync(sf, 'utf-8');
            if (badHashLinkPattern.test(content)) {
                offenders.push(path.basename(sf));
            }
        }

        expect(offenders.length, `Found data-sveltekit-reload used alongside hash (#) links in: ${offenders.join(', ')}. This breaks SPA translation reactivity!`).toBe(0);
    });
});
