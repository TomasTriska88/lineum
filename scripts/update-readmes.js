const fs = require('fs');
const path = require('path');

const whitepapersDir = path.join(__dirname, '../whitepapers');

// Helper to extract the Title and Status from a markdown file
function extractTitleAndStatus(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');
    let title = path.basename(filePath, '.md');
    let status = 'Unknown';

    let inFrontmatter = false;
    for (const line of lines) {
        if (line.trim() === '---') {
            inFrontmatter = !inFrontmatter;
            continue;
        }
        if (inFrontmatter && line.startsWith('Status:')) {
            status = line.split(':')[1].trim();
        } else if (line.startsWith('# ')) {
            title = line.replace('# ', '').trim();
            break; // Stop parsing after finding the H1 title
        }
    }
    return { title, status };
}

// Generate the sub-directory index tables
function processDirectory(dirPath, categoryName) {
    if (!fs.existsSync(dirPath)) return null;

    const files = fs.readdirSync(dirPath);
    const mdFiles = files.filter(f => f.endsWith('.md') && f !== 'README.md');

    let indexContent = `<!-- INDEX_START -->\n## 📚 Document Index\n\n| Document | Status | File |\n| :--- | :--- | :--- |\n`;

    if (mdFiles.length === 0) {
        indexContent += `| *(No documents yet)* | - | - |\n`;
    } else {
        for (const file of mdFiles) {
            const filePath = path.join(dirPath, file);
            const { title, status } = extractTitleAndStatus(filePath);
            const statusLower = status.toLowerCase();
            let badge = '⚠️ ' + status;
            if (statusLower.includes('retracted') || statusLower.includes('falsified')) badge = '🚫 ' + status;
            if (statusLower.includes('locked') || statusLower.includes('validated') || statusLower.includes('core')) badge = '🔒 ' + status;

            indexContent += `| **${title}** | ${badge} | \`${file}\` |\n`;
        }
    }
    indexContent += `<!-- INDEX_END -->`;

    const readmePath = path.join(dirPath, 'README.md');
    let readmeText = '';
    if (fs.existsSync(readmePath)) {
        readmeText = fs.readFileSync(readmePath, 'utf-8');
        // Replace existing index if it exists
        const startIdx = readmeText.indexOf('<!-- INDEX_START -->');
        const endIdx = readmeText.indexOf('<!-- INDEX_END -->');
        if (startIdx !== -1 && endIdx !== -1) {
            readmeText = readmeText.substring(0, startIdx) + indexContent + readmeText.substring(endIdx + '<!-- INDEX_END -->'.length);
        } else {
            // Append
            readmeText += '\n' + indexContent + '\n';
        }
    } else {
        // Create new README
        readmeText = `# ${categoryName}\n\nThis directory contains the ${categoryName} tier of the Lineum publication architecture.\n\n${indexContent}\n`;
    }

    const currentContent = fs.existsSync(readmePath) ? fs.readFileSync(readmePath, 'utf-8') : null;
    if (readmeText !== currentContent) {
        fs.writeFileSync(readmePath, readmeText);
    }

    return indexContent;
}

const dirs = [
    { dir: '1-core', name: 'Tier 1: Core' },
    { dir: '2-cosmology', name: 'Tier 2: Cosmology' },
    { dir: '3-ontology', name: 'Tier 3: Ontology' },
    { dir: '4-archive', name: 'Tier 4: Archive' }
];

console.log('Generating dynamic README indexes for the whitepapers...');

let masterIndex = `<!-- INDEX_START -->\n## 📚 Master Document Index\n\n`;

for (const d of dirs) {
    const fullPath = path.join(whitepapersDir, d.dir);
    const subIndex = processDirectory(fullPath, d.name);
    if (subIndex) {
        masterIndex += `### [${d.name}](./${d.dir}/)\n`;
        // Strip the HTML comments and H2 from sub-index before injecting to master
        let cleanSubIndex = subIndex
            .replace('<!-- INDEX_START -->\n', '')
            .replace('## 📚 Document Index\n\n', '')
            .replace('<!-- INDEX_END -->', '');
        masterIndex += cleanSubIndex + '\n';
    }
}
masterIndex += `<!-- INDEX_END -->`;

// Update main README
const mainReadmePath = path.join(whitepapersDir, 'README.md');
if (fs.existsSync(mainReadmePath)) {
    let text = fs.readFileSync(mainReadmePath, 'utf-8');
    const startIdx = text.indexOf('<!-- INDEX_START -->');
    const endIdx = text.indexOf('<!-- INDEX_END -->');

    const previousText = text;
    if (startIdx !== -1 && endIdx !== -1) {
        text = text.substring(0, startIdx) + masterIndex + text.substring(endIdx + '<!-- INDEX_END -->'.length);
    } else {
        text += '\n' + masterIndex + '\n';
    }
    if (text !== previousText) {
        fs.writeFileSync(mainReadmePath, text);
    }
}

console.log('✅ All whitepaper READMEs successfully updated!');
