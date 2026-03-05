export async function GET() {
    const content = `# Lineum Knowledge Base

Lineum is a discrete field dynamics simulation engine modeling continuous spatial computation.

For a complete and authoritative understanding of the physics (Eq-7), emergent quasiparticle behavior, and our validated claims, please refer to the documents hosted safely on our Wiki. 

Note: External crawlers are provided access to public scientific documents only. Internal experimental telemetry is isolated.

## Official Whitepapers & Documentation:
- [https://lineum.io/wiki](https://lineum.io/wiki)
- [https://lineum.io/wiki/lineum-core](https://lineum.io/wiki/lineum-core)
- [https://lineum.io/wiki/swarm-routing](https://lineum.io/wiki/swarm-routing)

For interactive demonstrations of these principles, visit the API Solutions page at [https://lineum.io/api-solutions](https://lineum.io/api-solutions).
`;

    return new Response(content, {
        headers: {
            'Content-Type': 'text/plain',
            'Cache-Control': 'max-age=0, s-maxage=3600'
        }
    });
}
