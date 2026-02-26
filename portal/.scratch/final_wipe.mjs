import fs from 'fs';

const langs = ['en', 'cs', 'de', 'ja'];

for (const lang of langs) {
    const file = `messages/${lang}.json`;
    if (fs.existsSync(file)) {
        const data = JSON.parse(fs.readFileSync(file, 'utf8'));
        for (const [key, text] of Object.entries(data)) {
            if (key.startsWith('lina_egg_') || key === 'lina_status_idle') {
                // Remove trailing period or Japanese period exclusively
                data[key] = text.replace(/[.。]+(\s*✨)?$/, '$1').trim();
            }
        }
        fs.writeFileSync(file, JSON.stringify(data, null, 2));
    }
}
console.log('Final wipe of periods complete on all existing messages.');
