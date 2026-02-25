import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load = (({ params }) => {
    const slug = params.slug;

    const data = {
        'urban-logistics': {
            title: 'Urban Traffic & Logistics',
            subtitle: 'Routing 10,000 agents without graph algorithms.',
            description: 'Traditional discrete routing (A*) collapses when calculating dynamic traffic for thousands of agents simultaneously. The Lineum Field processes entire cities in a single tensor operation.',
            heroColor: 'from-sky-500/20 to-transparent',
            accent: 'sky-400',
            problem: 'Graph algorithms scale poorly (O(N*logN)) for multiple agents. In dense urban grids, updating traffic values triggers cascading recalculations across the entire network.',
            solution: 'Lineum computes the resistance landscape globally in O(1). All agents simply flow down the gradient, reacting to congestion instantly without pathfinding overhead.',
            apiSnippet: `// Python Example
import requests

response = requests.post(
    "https://api.lineum-core.com/v1/compute/urban",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "map_geojson": "manhattan_grid.json",
        "agent_count": 50000,
        "dynamic_friction": True
    }
)
print(response.json())`
        },
        'crowd-evacuation': {
            title: 'Crowd Panic & Evacuation',
            subtitle: 'Real-time bottleneck prevention in stadiums.',
            description: 'Model massive crowd dynamics. Understand how physical constraints and panic behaviors lead to dangerous arching and crushing, and design exits that breathe.',
            heroColor: 'from-fuchsia-500/20 to-transparent',
            accent: 'fuchsia-400',
            problem: 'Evacuation modeling requires fluid-like equations combined with discrete agent goals. Standard shortest-path algorithms ignore the physical space agents take up, failing to predict lethal crushes.',
            solution: 'The Lineum spatial field models agents as repulsive density waves. Bottlenecks naturally emerge from the math, allowing architects to optimize hallways long before concrete is poured.',
            apiSnippet: `// JavaScript Example
const res = await fetch('https://api.lineum-core.com/v1/compute/evac', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    blueprint: 'stadium_layout.png',
    capacity: 85000,
    flow_rate_target: 3.5 // people per second per meter
  })
});
const report = await res.json();`
        },
        'hardware-routing': {
            title: 'Hardware & Dielectric Routing',
            subtitle: 'Finding optimal tracks on multi-layer PCBs.',
            description: 'Autorouting for complex printed circuit boards (PCBs) or VLSI chips. Lineum naturally finds non-intersecting, optimal trace paths around thousands of components.',
            heroColor: 'from-emerald-500/20 to-transparent',
            accent: 'emerald-400',
            problem: 'Traditional PCB autorouters use grid-based maze-solving (Lee algorithm), which scales terribly on high-density boards, often failing to find 100% completion.',
            solution: 'Lineum treats components as impenetrable barriers and traces as flowing rivers of current. The field inherently repels competing traces, finding harmonious layouts organically.',
            apiSnippet: `// Node.js
import { LineumClient } from '@lineum/sdk';

const client = new LineumClient(process.env.LINEUM_API_KEY);

const gerberResult = await client.routePCB({
  netlist: 'motherboard_nets.dsn',
  layers: 8,
  rules: {
    clearance: 0.1,    // mm
    trackWidth: 0.15   // mm
  }
});`
        }
    };

    if (slug in data) {
        return data[slug as keyof typeof data];
    }

    throw error(404, 'Domain scenario not found');
}) satisfies PageLoad;
