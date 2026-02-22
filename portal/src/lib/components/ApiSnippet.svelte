<script lang="ts">
    import { onMount } from "svelte";

    let activeTab: "python" | "node" | "curl" = "python";

    const snippets = {
        python: `import httpx
import websockets
import asyncio
import json

async def start_lineum_routing():
    # 1. Dispatch the routing task to the Lineum engine
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.lineum.io/route/task", json={
            "size": 128,
            "max_steps": 1000,
            "agents": [{"id": "Alpha", "start": {"x": 10, "y": 10}}],
            "target": {"x": 110, "y": 110}
        }, headers={"Authorization": "Bearer YOUR_API_KEY"})
        
        task_id = res.json()["task_id"]

    # 2. Connect to the high-throughput fluid stream
    async with websockets.connect(f"wss://api.lineum.io/route/stream/{task_id}") as ws:
        async for message in ws:
            data = json.loads(message)
            if "paths" in data:
                print(f"Step {data['step']}: Agent positions updated")
                # Pipe exactly where agents should move

asyncio.run(start_lineum_routing())`,
        node: `import WebSocket from 'ws';

async function startLineumRouting() {
    // 1. Dispatch the routing task to the Lineum engine
    const res = await fetch("https://api.lineum.io/route/task", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_API_KEY"
        },
        body: JSON.stringify({
            size: 128, max_steps: 1000,
            agents: [{ id: "Alpha", start: { x: 10, y: 10 } }],
            target: { x: 110, y: 110 }
        })
    });
    
    const { task_id } = await res.json();

    // 2. Connect to the high-throughput fluid stream
    const ws = new WebSocket(\`wss://api.lineum.io/route/stream/\${task_id}\`);
    
    ws.on('message', (data) => {
        const msg = JSON.parse(data);
        if (msg.paths) {
            console.log(\`Step \${msg.step}: Agent positions updated\`);
            // Pipe exactly where agents should move
        }
    });
}

startLineumRouting();`,
        curl: `# 1. Dispatch the routing task to the Lineum engine
curl -X POST https://api.lineum.io/route/task \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -d '{
    "size": 128,
    "max_steps": 1000,
    "agents": [{"id": "Alpha", "start": {"x": 10, "y": 10}}],
    "target": {"x": 110, "y": 110}
  }'

# Returns: { "task_id": "req_8f72a..." }

# 2. Connect to the WebSocket stream using your preferred client
# wss://api.lineum.io/route/stream/req_8f72a...`,
    };

    let copied = false;

    function copyToClipboard() {
        navigator.clipboard.writeText(snippets[activeTab]);
        copied = true;
        setTimeout(() => (copied = false), 2000);
    }
</script>

<div class="w-full max-w-5xl mx-auto mb-32 flex flex-col items-center">
    <div class="text-center mb-12">
        <h3 class="text-3xl md:text-5xl font-bold text-white mb-6">
            Developer Experience First
        </h3>
        <p
            class="text-slate-400 text-lg md:text-xl font-light max-w-3xl mx-auto"
        >
            Harness the power of fluid dynamics with just <strong
                class="text-white">two API calls</strong
            >. No complex physics or discrete math required. We handle the heavy
            continuous field tensors, you just receive the optimal paths.
        </p>
    </div>

    <div
        class="w-full bg-[#0d1117] border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col md:flex-row"
    >
        <!-- Left Sidebar (Tabs) -->
        <div
            class="w-full md:w-48 bg-slate-900/50 border-b md:border-b-0 md:border-r border-slate-800 flex flex-row md:flex-col items-start justify-start p-4 gap-2 shrink-0 overflow-x-auto"
        >
            <button
                class="w-full text-left px-4 py-2.5 rounded-lg font-mono text-sm transition-all whitespace-nowrap {activeTab ===
                'python'
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 border border-transparent'}"
                on:click={() => (activeTab = "python")}
            >
                Python (async)
            </button>
            <button
                class="w-full text-left px-4 py-2.5 rounded-lg font-mono text-sm transition-all whitespace-nowrap {activeTab ===
                'node'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 border border-transparent'}"
                on:click={() => (activeTab = "node")}
            >
                Node.js
            </button>
            <button
                class="w-full text-left px-4 py-2.5 rounded-lg font-mono text-sm transition-all whitespace-nowrap {activeTab ===
                'curl'
                    ? 'bg-violet-500/10 text-violet-400 border border-violet-500/30'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 border border-transparent'}"
                on:click={() => (activeTab = "curl")}
            >
                cURL
            </button>
        </div>

        <!-- Right Code Editor -->
        <div class="flex-grow w-full relative">
            <div class="absolute top-4 right-4 z-10">
                <button
                    class="px-3 py-1.5 rounded-md bg-slate-800/50 border border-slate-700 text-slate-400 text-xs font-mono hover:bg-slate-700 hover:text-white transition-all flex items-center gap-2"
                    on:click={copyToClipboard}
                >
                    {#if copied}
                        <span class="text-emerald-400">Copied!</span>
                    {:else}
                        Copy
                    {/if}
                </button>
            </div>

            <div class="p-6 md:p-8 overflow-x-auto w-full">
                <pre
                    class="font-mono text-sm text-slate-300 leading-relaxed min-w-[500px]"><code
                        >{snippets[activeTab]}</code
                    ></pre>
            </div>
        </div>
    </div>
</div>
