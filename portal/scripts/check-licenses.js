import checker from 'license-checker-rseidelsohn';
import path from 'path';

const FORBIDDEN_LICENSES = [
    'GPL',
    'GPL-2.0',
    'GPL-3.0',
    'AGPL',
    'AGPL-3.0',
    'LGPL'
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
