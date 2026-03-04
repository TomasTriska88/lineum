<script lang="ts">
    import { onMount } from "svelte";
    import { slide } from "svelte/transition";

    // The frontend retains state, isolating the LLM from conversational history.
    let sessionId = $state("");
    let currentMode: "phys" | "hybrid" = $state("phys");
    let currentText = $state("");
    let isInjecting = $state(false);

    interface InteractionTurn {
        turnId: string;
        timestamp: string;
        input_x: string;
        mode: "phys" | "hybrid";
        metrics: {
            max_psi: number;
            mean_pressure: number;
        };
        readout_r: number[]; // Length: 200
        broca_model: string | null;
        broca_text: string | null;
    }

    let auditFeed: InteractionTurn[] = $state([]);

    let isInitializing = $state(true);

    onMount(async () => {
        // Generate an isolated session ID for this window instance.
        sessionId = crypto.randomUUID();

        try {
            // Wake up Lina so the physical engine loop begins
            await fetch("http://127.0.0.1:8000/entity/wake", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ entity_id: "lina", grid_size: 100 }),
            });
        } catch (e) {
            console.error("Failed to wake entity:", e);
        } finally {
            isInitializing = false;
        }
    });

    async function handleInject() {
        if (!currentText.trim() || isInjecting) return;

        isInjecting = true;
        const payload = {
            session_id: sessionId,
            mode: currentMode,
            message: currentText,
        };

        // Keep a local reference to the text before clearing the input box
        const injectedText = currentText;
        currentText = "";

        try {
            // Connect to the FastAPI routing_backend
            const res = await fetch("http://127.0.0.1:8000/entity/lina/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!res.ok) throw new Error(`API Error: ${res.statusText}`);

            const data = await res.json();

            // Construct the TurnCard data
            const turn: InteractionTurn = {
                turnId: crypto.randomUUID(),
                timestamp: new Date().toISOString(),
                input_x: injectedText,
                mode: currentMode,
                metrics: {
                    max_psi: data.metrics?.max_psi ?? 0,
                    mean_pressure: data.metrics?.mean_pressure ?? 0,
                },
                readout_r: data.readout_r ?? [],
                broca_model:
                    data.mode === "hybrid"
                        ? data.broca_model_name || "local-model"
                        : null,
                broca_text:
                    data.mode === "hybrid" ? data.broca_output_text : null,
            };

            auditFeed = [...auditFeed, turn];

            // Auto scroll to bottom of audit feed could be added here
        } catch (e) {
            console.error("Injection failed:", e);
            alert(
                "Failed to inject semantics into Eq-4'. Is the backend running?",
            );
        } finally {
            isInjecting = false;
        }
    }

    function replayTurn(turn: InteractionTurn) {
        currentText = turn.input_x;
        currentMode = turn.mode;
        handleInject();
    }

    function saveTrace(turn: InteractionTurn) {
        const blob = new Blob([JSON.stringify(turn, null, 2)], {
            type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `trace_${sessionId.slice(0, 8)}_${turn.turnId.slice(0, 8)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
</script>

<div
    class="flex h-[calc(100vh-100px)] w-full bg-slate-950 text-slate-300 font-mono overflow-hidden"
>
    <!-- LEFT COLUMN: Action & Real-time State -->
    <section class="w-1/2 flex flex-col border-r border-slate-700/50 p-4">
        <header class="mb-3">
            <h1
                class="text-lg font-bold text-slate-100 uppercase tracking-widest mb-1"
            >
                Explorer
            </h1>
            <div
                class="text-[10px] text-slate-500 uppercase tracking-widest flex items-center justify-between"
            >
                <span>Eq-4' Stabilized Runtime</span>
                <span
                    class="bg-indigo-900/40 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20"
                    >Session: {sessionId.slice(0, 8)}</span
                >
            </div>
        </header>

        <!-- Visualizer Canvas Placeholder -->
        <div
            class="flex-grow bg-slate-900 rounded border border-slate-800 mb-4 flex items-center justify-center overflow-hidden relative min-h-[150px]"
        >
            <div
                class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-800/20 via-slate-900/0 to-transparent"
            ></div>
            <!-- TODO: Integrate WebGL/FieldShader.svelte here -->
            <div class="text-center">
                <div class="text-4xl mb-2 opacity-10 font-light">R</div>
                <div class="text-xs text-slate-600 uppercase tracking-widest">
                    Awaiting topological mount
                </div>
            </div>
        </div>

        <!-- Input Console -->
        <div
            class="bg-slate-900/50 p-3 rounded border border-slate-800 backdrop-blur-sm shrink-0"
        >
            <div
                class="flex items-center justify-between mb-3 pb-3 border-b border-slate-700/50"
            >
                <div>
                    <div class="text-xs font-semibold text-slate-200">
                        Translation Layer
                    </div>
                    <div class="text-[10px] text-slate-500">
                        Determines if 'Mouth' passes R to LLM
                    </div>
                </div>

                <!-- Mode Switch (Guardrail) -->
                <button
                    type="button"
                    class="relative inline-flex h-6 w-40 shrink-0 cursor-pointer rounded-full border border-slate-600 transition-colors duration-200 ease-in-out focus:outline-none {currentMode ===
                    'hybrid'
                        ? 'bg-indigo-600'
                        : 'bg-slate-700'}"
                    onclick={() =>
                        (currentMode =
                            currentMode === "hybrid" ? "phys" : "hybrid")}
                >
                    <span class="sr-only">Toggle translation mode</span>
                    <span
                        class="absolute inset-0 flex h-full w-full items-center justify-center transition-opacity"
                    >
                        <span
                            class="text-[10px] font-bold {currentMode === 'phys'
                                ? 'text-slate-300 ml-5'
                                : 'text-indigo-100 mr-5'}"
                        >
                            {currentMode === "phys"
                                ? "RAW PHYSICS"
                                : "VOICE ON"}
                        </span>
                    </span>
                    <span
                        class="pointer-events-none absolute left-[1px] top-[1px] inline-block h-[20px] w-[20px] transform rounded-full bg-slate-200 shadow ring-0 transition duration-200 ease-in-out {currentMode ===
                        'hybrid'
                            ? 'translate-x-[134px]'
                            : 'translate-x-0'}"
                    ></span>
                </button>
            </div>

            <div class="flex gap-2">
                <input
                    type="text"
                    class="flex-grow bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-sans disabled:opacity-50 disabled:cursor-not-allowed"
                    placeholder="Inject semantic perturbation (X)..."
                    bind:value={currentText}
                    onkeydown={(e) => e.key === "Enter" && handleInject()}
                    disabled={isInjecting || isInitializing}
                />
                <button
                    class="px-4 py-1.5 bg-slate-200 text-slate-900 font-bold uppercase tracking-wider text-xs rounded hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed w-[90px]"
                    onclick={handleInject}
                    disabled={isInjecting || isInitializing}
                >
                    {isInitializing
                        ? "Waking..."
                        : isInjecting
                          ? "Wait"
                          : "Inject"}
                </button>
            </div>
        </div>
    </section>

    <!-- RIGHT COLUMN: Audit Feed (Ground Truth Trail) -->
    <section class="w-1/2 flex flex-col bg-slate-900 overflow-y-auto relative">
        <header
            class="sticky top-0 bg-slate-900/95 backdrop-blur-md z-10 border-b border-slate-700/50 p-4 flex justify-between items-center shadow-sm"
        >
            <h2
                class="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2"
            >
                <span
                    class="w-1.5 h-1.5 rounded-full bg-emerald-500 bg-opacity-80"
                ></span>
                Ground Truth Audit
            </h2>
            <div class="text-[10px] text-slate-500">Temporal sequence</div>
        </header>

        <div class="p-4 space-y-4 flex-grow">
            {#if auditFeed.length === 0}
                <div
                    class="h-full flex flex-col items-center justify-center text-slate-600 pb-20 mt-20"
                >
                    <div
                        class="w-12 h-12 border border-slate-700 border-dashed rounded-full flex items-center justify-center mb-3 opacity-50"
                    >
                        <svg
                            class="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            ><path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M13 10V3L4 14h7v7l9-11h-7z"
                            ></path></svg
                        >
                    </div>
                    <p class="text-xs text-center font-light leading-relaxed">
                        The matrix is silent.<br />Awaiting first semantic
                        perturbation.
                    </p>
                </div>
            {/if}

            {#each auditFeed as turn (turn.turnId)}
                <div
                    class="bg-slate-950 border border-slate-800 rounded overflow-hidden shadow-lg"
                    transition:slide
                >
                    <!-- Catalyst Header -->
                    <div
                        class="bg-slate-800/30 px-4 py-3 border-b border-slate-800"
                    >
                        <div class="text-[10px] text-slate-500 mb-1 font-mono">
                            {new Date(turn.timestamp).toLocaleTimeString()} · {turn.turnId.slice(
                                0,
                                8,
                            )}
                        </div>
                        <div
                            class="text-base text-slate-200 font-sans italic break-words"
                        >
                            "{turn.input_x}"
                        </div>
                    </div>

                    <!-- Ground Truth Metrics -->
                    <div class="px-4 py-3 border-b border-slate-800/80">
                        <div
                            class="text-[10px] font-bold text-emerald-600/80 uppercase tracking-widest mb-2 flex items-center gap-1.5"
                        >
                            <svg
                                class="w-3 h-3"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                                ></path></svg
                            >
                            Eq-4' Physical State
                        </div>
                        <div class="grid grid-cols-3 gap-2 mb-3">
                            <div
                                class="bg-slate-900 rounded p-1.5 border border-slate-800/30 text-center"
                            >
                                <div
                                    class="text-[8px] text-slate-500 uppercase"
                                >
                                    Max Psi (Tension)
                                </div>
                                <div
                                    class="text-sm text-emerald-400 font-light"
                                >
                                    {turn.metrics.max_psi.toFixed(4)}
                                </div>
                            </div>
                            <div
                                class="bg-slate-900 rounded p-1.5 border border-slate-800/30 text-center"
                            >
                                <div
                                    class="text-[8px] text-slate-500 uppercase"
                                >
                                    Mean Pressure (Phi)
                                </div>
                                <div
                                    class="text-sm text-emerald-400 font-light"
                                >
                                    {turn.metrics.mean_pressure.toFixed(4)}
                                </div>
                            </div>
                            <div
                                class="bg-slate-900 rounded p-1.5 border border-slate-800/30 text-center"
                            >
                                <div
                                    class="text-[8px] text-slate-500 uppercase"
                                >
                                    R Vector Sum
                                </div>
                                <div class="text-sm text-slate-300 font-light">
                                    {turn.readout_r
                                        .reduce((a, b) => a + b, 0)
                                        .toFixed(2)}
                                </div>
                            </div>
                        </div>
                        <details class="group">
                            <summary
                                class="text-[10px] text-slate-500 cursor-pointer hover:text-slate-300 transition-colors select-none flex items-center inline-block"
                            >
                                <span
                                    class="border border-slate-700/50 rounded px-1.5 py-0.5 group-open:bg-slate-800/50"
                                    >Inspect R-Vector Fingerprint</span
                                >
                            </summary>
                            <div
                                class="mt-2 p-2 bg-black/40 rounded border border-slate-800 font-mono text-[9px] text-slate-600 leading-snug overflow-x-auto break-all max-h-24 overflow-y-auto"
                            >
                                [{turn.readout_r
                                    .map((n) => n.toFixed(3))
                                    .join(", ")}]
                            </div>
                        </details>
                    </div>

                    <!-- Translation Layer (Only if Hybrid) -->
                    {#if turn.mode === "hybrid"}
                        <div
                            class="px-4 py-3 bg-indigo-950/10 border-b border-indigo-900/20"
                        >
                            <div
                                class="text-[10px] font-bold text-indigo-400/80 uppercase tracking-widest mb-2 flex items-center gap-1.5"
                            >
                                <svg
                                    class="w-3 h-3"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                    ><path
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="2"
                                        d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                                    ></path></svg
                                >
                                Broca Translation
                                <span
                                    class="bg-indigo-900/30 text-[8px] px-1.5 py-0.5 rounded border border-indigo-700/30 ml-auto"
                                    >{turn.broca_model}</span
                                >
                            </div>
                            <p
                                class="text-slate-300 font-sans leading-relaxed text-sm pl-3 border-l-2 border-indigo-500/20 break-words"
                            >
                                {turn.broca_text}
                            </p>
                        </div>
                    {/if}

                    <!-- Audit Action Footer -->
                    <div
                        class="px-3 py-2 bg-slate-900/30 flex justify-end gap-3"
                    >
                        <button
                            class="text-[10px] text-slate-500 hover:text-white uppercase tracking-widest flex items-center gap-1 transition-colors"
                            onclick={() => replayTurn(turn)}
                        >
                            <svg
                                class="w-2.5 h-2.5"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                                ></path></svg
                            >
                            Replay
                        </button>
                        <button
                            class="text-[10px] text-emerald-500/60 hover:text-emerald-400 uppercase tracking-widest flex items-center gap-1 transition-colors"
                            onclick={() => saveTrace(turn)}
                        >
                            <svg
                                class="w-2.5 h-2.5"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                ><path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                                ></path></svg
                            >
                            Save JSON
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    </section>
</div>
