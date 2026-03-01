import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';

export async function load() {
    let doi = '10.5281/zenodo.16934359'; // Fallback

    try {
        const cffPath = resolve('src/lib/data/project/CITATION.cff');
        if (existsSync(cffPath)) {
            const fileContents = readFileSync(cffPath, 'utf8');
            // Extract the DOI via regex to avoid heavy YAML parser dependencies with viral licenses
            const doiMatch = fileContents.match(/^doi:\s*([^\r\n]+)/m);
            if (doiMatch && doiMatch[1]) {
                doi = doiMatch[1].trim();
            }
        }
    } catch (e) {
        console.error('Error loading CITATION.cff for DOI:', e);
    }

    return {
        doi
    };
}
