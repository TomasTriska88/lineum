export async function GET() {
    const pages = [
        { loc: 'https://lineum.io/', priority: 1.0, changefreq: 'daily' },
        { loc: 'https://lineum.io/wiki', priority: 0.9, changefreq: 'weekly' },
        { loc: 'https://lineum.io/api-solutions', priority: 0.8, changefreq: 'weekly' },
        { loc: 'https://simulacrum.lineum.io/', priority: 0.8, changefreq: 'monthly' },
        { loc: 'https://lineum.io/about', priority: 0.6, changefreq: 'monthly' }
    ];

    const langs = ['en', 'cs', 'de', 'ja'];

    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${pages.map(page => `    <url>
        <loc>${page.loc}</loc>
        <changefreq>${page.changefreq}</changefreq>
        <priority>${page.priority}</priority>
${langs.map(lang => `        <xhtml:link rel="alternate" hreflang="${lang}" href="${page.loc}" />`).join('\n')}
    </url>`).join("\n")}
</urlset>`;

    return new Response(sitemap, {
        headers: {
            'Content-Type': 'application/xml',
            'Cache-Control': 'max-age=0, s-maxage=3600'
        }
    });
}
