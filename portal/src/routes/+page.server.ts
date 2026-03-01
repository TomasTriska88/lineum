import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';
import yaml from 'js-yaml';

export async function load() {
    let doi = '10.5281/zenodo.16934359'; // Fallback

    try {
        const cffPath = resolve('src/lib/data/project/CITATION.cff');
        if (existsSync(cffPath)) {
            const fileContents = readFileSync(cffPath, 'utf8');
            const data = yaml.load(fileContents) as any;
            if (data && data.doi) {
                doi = data.doi;
            }
        }
    } catch (e) {
        console.error('Error loading CITATION.cff for DOI:', e);
    }

    return {
        doi
    };
}
