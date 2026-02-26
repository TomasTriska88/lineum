import fs from 'fs';

['cs', 'en', 'de', 'ja'].forEach(lang => {
    const p = 'messages/' + lang + '.json';
    const data = JSON.parse(fs.readFileSync(p, 'utf-8'));
    for (let k in data) {
        if (k.startsWith('lina_egg_') || k === 'lina_status_idle') {
            data[k] = data[k].replace(/[.!?。！]+(\s*✨)?$/, '$1').trim();
        }
    }
    fs.writeFileSync(p, JSON.stringify(data, null, 2));
});
console.log('Dots removed successfully');
