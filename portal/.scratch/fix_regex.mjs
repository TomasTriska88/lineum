import fs from 'fs';

let content = fs.readFileSync('.scratch/build_eggs_all.mjs', 'utf8');

content = content.replace(
    / \* 3\. NO TRAILING PUNCTUATION:[\s\S]*?breaks the illusion\./,
    ` * 3. NO TRAILING PERIODS:\n *    Do NOT put periods (.) or Japanese periods (。) at the end of the strings. \n *    The UI automatically appends a blinking terminal cursor directly after the \n *    last character, and trailing periods break the illusion. Question marks (?) \n *    and exclamation marks (!) are acceptable and can be kept.`
);

content = content.replace(
    /for \(const \[key, trans\] of Object\.entries\(eggsObj\)\) \{\n\s*data\[key\] = trans\[lang\];\n\s*\}/,
    `for (const [key, trans] of Object.entries(eggsObj)) {\n        const rawText = trans[lang] || trans['en'] || "";\n        data[key] = rawText.replace(/[.。]+(\\s*✨)?$/, '$1').trim();\n    }`
);

fs.writeFileSync('.scratch/build_eggs_all.mjs', content);
console.log('Regex and fallback applied.');
