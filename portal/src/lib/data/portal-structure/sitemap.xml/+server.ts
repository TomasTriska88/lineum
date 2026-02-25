export async function GET() {
    const pages = [
        { loc: 'https://lineum.io/', priority: 1.0, changefreq: 'daily' },
        { loc: 'https://lineum.io/wiki', priority: 0.9, changefreq: 'weekly' },
        { loc: 'https://lineum.io/api-solutions', priority: 0.8, changefreq: 'weekly' },
        { loc: 'https://simulacrum.lineum.io/', priority: 0.8, changefreq: 'monthly' }
    ];

    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(page => `    <url>
        <loc>${page.loc}</loc>
        <changefreq>${page.changefreq}</changefreq>
        <priority>${page.priority}</priority>
    </url>`).join("\n")}
</urlset>`;

    return new Response(sitemap, {
        headers: {
            'Content-Type': 'application/xml',
            'Cache-Control': 'max-age=0, s-maxage=3600'
        }
    });
}
