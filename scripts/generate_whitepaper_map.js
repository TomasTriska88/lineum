const fs = require('fs');
const path = require('path');

/**
 * Automates the generation of whitepaper_map.json
 * Scans the whitepapers directory and creates relative paths from the repo root
 */

function getAllMdFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {
            // Recurse into subdirectories
            getAllMdFiles(filePath, fileList);
        } else if (file.endsWith('.md')) {
            fileList.push(filePath);
        }
    }
    return fileList;
}

function generateMap(whitepapersDir, repoRoot) {
    const mdFiles = getAllMdFiles(whitepapersDir);
    const map = {};

    for (const filePath of mdFiles) {
        const filename = path.basename(filePath);
        
        // Exclude specific files
        if (filename === 'TODO.md' || filename === 'TEMPLATE.md') {
            continue;
        }

        // Create relative path using POSIX separators for cross-platform compatibility
        const relativePath = path.relative(repoRoot, filePath).split(path.sep).join('/');
        map[filename] = relativePath;
    }

    return map;
}

function run() {
    // Determine canonical absolute paths
    const repoRoot = path.resolve(__dirname, '..');
    const whitepapersDir = path.join(repoRoot, 'whitepapers');
    const outputPath = path.join(repoRoot, 'lab', 'src', 'lib', 'data', 'whitepaper_map.json');

    console.log(`[Whitepaper Map] Indexing ${whitepapersDir} ...`);
    
    if (!fs.existsSync(whitepapersDir)) {
        console.error(`[Whitepaper Map] Error: Cannot find whitepapers directory at ${whitepapersDir}`);
        process.exit(1);
    }

    const map = generateMap(whitepapersDir, repoRoot);
    const entriesCount = Object.keys(map).length;

    console.log(`[Whitepaper Map] Found ${entriesCount} valid .md documents.`);
    
    // Write back to the map file atomically
    fs.writeFileSync(outputPath, JSON.stringify(map, null, 2), 'utf8');
    console.log(`[Whitepaper Map] Successfully updated ${outputPath}`);
}

// Support for running as a script vs being imported for tests
if (require.main === module) {
    run();
} else {
    module.exports = { getAllMdFiles, generateMap };
}
