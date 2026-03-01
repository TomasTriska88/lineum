import * as checker from 'license-checker-rseidelsohn';
import path from 'path';

const FORBIDDEN_LICENSES = [
    // 1. Classic Strong Copyleft (Viral)
    'GPL', 'GPL-2.0', 'GPL-3.0',
    'AGPL', 'AGPL-1.0', 'AGPL-3.0',
    'LGPL', 'LGPL-2.0', 'LGPL-2.1', 'LGPL-3.0',

    // 2. Alternative Strong Copyleft
    'OSL-3.0', 'EUPL-1.1', 'EUPL-1.2',
    'Sleepycat',
    'CC-BY-SA-4.0', 'CC-BY-SA-3.0',

    // 3. Source-Available / Non-Commercial Traps
    'SSPL-1.0', 'BSL-1.1', 'Commons-Clause',

    // 4. Weak Copyleft / File-level (Often rejected by corporate legal)
    'CDDL-1.0', 'CDDL-1.1',
    'EPL-1.0', 'EPL-2.0',
    'MPL-1.1', 'MPL-2.0',

    // 5. Legal Grey Areas & "Joke" Licenses (Massive liability risk)
    'WTFPL', 'Beerware', 'Public Domain', 'Unlicense',

    // 6. No License / Proprietary Traps
    'UNLICENSED'
];

checker.init({
    start: path.resolve('./'),
    excludePrivatePackages: true,
    failOn: FORBIDDEN_LICENSES.join(';')
}, function (err, packages) {
    if (err) {
        console.error('\n🚨 FATAL LICENSE ERROR: Viral Open-Source License Detected! 🚨');
        console.error(err.message);
        console.error('You cannot use this dependency in the proprietary portal. Build aborted.\n');
        process.exit(1);
    } else {
        console.log('✅ License Check Passed: No viral GPL/AGPL dependencies found in the portal.');
        process.exit(0);
    }
});
