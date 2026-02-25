import { i18n } from "$lib/i18n";

export async function GET() {
    const pages = [
        { loc: '/', priority: 1.0, changefreq: 'daily' },
        { loc: '/wiki', priority: 0.9, changefreq: 'weekly' },
        { loc: '/api-solutions', priority: 0.8, changefreq: 'weekly' },
        { loc: '/simulacrum', priority: 0.8, changefreq: 'monthly' },
        { loc: '/about', priority: 0.6, changefreq: 'monthly' }
    ];

    const langs = ['en', 'cs', 'de', 'ja'] as const;
    const baseUrl = 'https://lineum.io';

    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${pages.map(page => `    <url>
        <loc>${baseUrl}${i18n.resolveRoute(page.loc, 'en')}</loc>
        <changefreq>${page.changefreq}</changefreq>
        <priority>${page.priority}</priority>
${langs.map(lang => `        <xhtml:link rel="alternate" hreflang="${lang}" href="${baseUrl}${i18n.resolveRoute(page.loc, lang)}" />`).join('\n')}
    </url>`).join("\n")}
</urlset>`;

    return new Response(sitemap, {
        headers: {
            'Content-Type': 'application/xml',
            'Cache-Control': 'max-age=0, s-maxage=3600'
        }
    });
}
