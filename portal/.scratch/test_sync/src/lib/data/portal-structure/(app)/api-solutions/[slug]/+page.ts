import { error } from '@sveltejs/kit';

export const load = ({ params }: { params: { slug: string } }) => {
  const slug = params.slug;

  const data = {
    'urban-logistics': {
      scenarioKey: 'urban',
      heroColor: 'from-sky-500/20 to-transparent',
      accent: 'sky-400',
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
      scenarioKey: 'evac',
      heroColor: 'from-fuchsia-500/20 to-transparent',
      accent: 'fuchsia-400',
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
      scenarioKey: 'hardware',
      heroColor: 'from-emerald-500/20 to-transparent',
      accent: 'emerald-400',
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
    },
    'true-rng': {
      scenarioKey: 'rng',
      heroColor: 'from-rose-500/20 to-transparent',
      accent: 'rose-400',
      apiSnippet: `// Python Example
import requests

response = requests.post(
    "https://api.lineum-core.com/v1/rng",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "resolution": 64,
        "pump_cycles": 1500
    }
)
print("True Hex Stream:", response.json()["hex_output"])`
    }
  };

  if (slug in data) {
    return { slug, ...data[slug as keyof typeof data] };
  }

  throw error(404, 'Not found');
};
