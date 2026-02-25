const fs = require('fs');

let content = fs.readFileSync('src/lib/i18n.ts', 'utf-8');

content = content.replace(/import {.*?} from 'svelte\/store';/, '');
content = content.replace('export const translations = ', 'const translations = ');
content = content.replace(/export const t = .*/s, '');
content = content.replace(/export const locale = .*/s, '');

content += `
; // Zajištění, že předchozí prohlášení bylo ukončeno

function flattenObject(obj, prefix = '') {
    let acc = {};
    for (let k in obj) {
        const pre = prefix.length ? prefix + '.' : '';
        if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
            Object.assign(acc, flattenObject(obj[k], pre + k));
        } else if (Array.isArray(obj[k])) {
            obj[k].forEach((item, index) => {
                if (typeof item === 'object') {
                    Object.assign(acc, flattenObject(item, pre + k + '.' + index));
                } else {
                    acc[pre + k + '.' + index] = item;
                }
            });
        } else {
            acc[pre + k] = obj[k];
        }
    }
    return acc;
}

const langs = ['cs', 'en', 'de', 'ja'];
for (let i = 0; i < langs.length; i++) {
    const lang = langs[i];
    const flat = flattenObject(translations[lang]);
    let output = {
        $schema: "https://inlang.com/schema/inlang-message-format"
    };
    for (let key in flat) {
        let safeKey = key.replace(/\\./g, '_');
        output[safeKey] = flat[key];
    }
    fs.writeFileSync('messages/' + lang + '.json', JSON.stringify(output, null, 2));
}
console.log('Successfully flattened JSON messages for Paraglide!');
`;

try {
    const fn = new Function('fs', content);
    fn(fs);
} catch (e) {
    console.error('Failed execution:', e);
}
