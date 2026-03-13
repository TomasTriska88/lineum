import { describe, it, expect } from 'vitest';
import { existsSync } from 'fs';
import { join } from 'path';

describe('Paraglide Generation Guard', () => {
    it('ensures Paraglide translation outputs are successfully generated before Vitest UI tests run', () => {
        const paraglidePath = join(process.cwd(), 'src', 'lib', 'paraglide', 'messages.js');
        const exists = existsSync(paraglidePath);
        expect(exists, 'PARAGLIDE GENERATION FAILED: The required translation file $lib/paraglide/messages.js is missing. This means the npx paraglide-js compile hook was bypassed or failed in CI.').toBe(true);
    });
});
