import fs from 'fs';
import path from 'path';

const PKG_PATH = path.resolve(process.cwd(), 'package.json');

function generateVersion() {
    const now = new Date();
    // UTC Timestamp format: YYYY.MM.DD-HHMM
    const year = now.getUTCFullYear();
    const month = String(now.getUTCMonth() + 1).padStart(2, '0');
    const day = String(now.getUTCDate()).padStart(2, '0');
    const hours = String(now.getUTCHours()).padStart(2, '0');
    const minutes = String(now.getUTCMinutes()).padStart(2, '0');

    return `${year}.${month}.${day}-${hours}${minutes}`;
}

const newVersion = generateVersion();
const pkg = JSON.parse(fs.readFileSync(PKG_PATH, 'utf-8'));

console.log(`[CalVer] Bumping portal version from ${pkg.version} to ${newVersion}`);
pkg.version = newVersion;

fs.writeFileSync(PKG_PATH, JSON.stringify(pkg, null, '\t') + '\n');
