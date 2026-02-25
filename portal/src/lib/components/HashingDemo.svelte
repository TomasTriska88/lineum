<script>
    import { t } from "$lib/i18n";
</script>

<div class="demo-container">
    <div class="header">
        <h2>SPATIAL AVALANCHE HASHING</h2>
        <p>
            One-way cryptographic spatial hashing. A 1-byte payload change
            rigorously triggers massive topological macro-fractures in the
            simulated fluid field.
        </p>
    </div>

    <div class="workspace">
        <div class="panel controls-panel">
            <h3>INPUT PAYLOAD</h3>
            <p class="desc">
                Enter text or upload a file. The fluid field will interpret the
                bit sequence as topographic obstacles.
            </p>

            <textarea
                class="payload-input"
                placeholder="Enter string to hash..."
                disabled
            ></textarea>

            <button class="generate-btn" disabled>
                INITIALIZE FLUID FIELD
            </button>
            <div class="coming-soon">
                <span class="pulse"></span>
                <span>SYSTEM UPGRADE PENDING</span>
            </div>

            <div class="stats mt-4">
                <div class="stat">
                    <span class="label">AVALANCHE RESOLUTION:</span>
                    <span class="val">256-bit</span>
                </div>
                <div class="stat">
                    <span class="label">COLLISION RATE:</span>
                    <span class="val">0.0000%</span>
                </div>
            </div>
        </div>

        <div class="panel visual-panel relative group">
            <div
                class="absolute inset-0 bg-[url('/noise.png')] opacity-10 mix-blend-overlay"
            ></div>
            <div
                class="flex flex-col items-center justify-center h-full opacity-50 relative z-10"
            >
                <svg
                    class="w-16 h-16 text-emerald-500 mb-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="1.5"
                        d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                </svg>
                <div class="font-mono text-emerald-400 tracking-widest text-sm">
                    FIELD LOCKED
                </div>
            </div>
        </div>

        <div class="panel terminal-panel relative">
            <h4>OUTPUT HASH (Base64)</h4>
            <div class="terminal flex items-center justify-center opacity-50">
                <div
                    class="text-emerald-500/50 font-mono text-xs text-center border border-emerald-500/20 p-4 rounded bg-emerald-500/5"
                >
                    AWAITING INFRASTRUCTURE DEPLOYMENT
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .demo-container {
        padding: 40px;
        color: #fff;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
        font-family: var(--font-mono, monospace);
    }

    .header h2 {
        margin: 0 0 10px 0;
        font-weight: bold;
        letter-spacing: 4px;
        color: #10b981; /* emerald-500 */
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        font-family: var(--font-sans, sans-serif);
    }

    .header p {
        margin: 0;
        font-size: 0.9rem;
        color: #aaa;
        margin-bottom: 20px;
        max-width: 600px;
    }

    .workspace {
        display: flex;
        gap: 30px;
        flex: 1;
        align-items: stretch;
    }

    .panel {
        background: rgba(0, 10, 5, 0.8);
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.05);
        padding: 25px;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
    }

    .controls-panel {
        width: 300px;
    }

    .visual-panel {
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.5);
        flex: 1.5;
        border: 1px dashed rgba(16, 185, 129, 0.3);
    }

    .terminal-panel {
        flex: 1;
    }

    h3 {
        margin: 0 0 10px 0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #888;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 5px;
    }

    h4 {
        margin: 0 0 15px 0;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #10b981;
        background: rgba(16, 185, 129, 0.1);
        padding: 4px 10px;
        border-left: 3px solid #10b981;
    }

    .desc {
        color: #bbb;
        font-size: 0.8rem;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    .payload-input {
        background: #000;
        border: 1px solid #333;
        color: #10b981;
        padding: 10px;
        font-family: inherit;
        font-size: 0.8rem;
        resize: none;
        height: 80px;
        margin-bottom: 15px;
        opacity: 0.5;
    }

    .generate-btn {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        font-weight: bold;
        text-align: center;
        letter-spacing: 1px;
        padding: 15px;
        border: 1px solid rgba(16, 185, 129, 0.5);
        cursor: not-allowed;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .coming-soon {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        color: #10b981;
        font-size: 0.7rem;
        font-weight: bold;
        letter-spacing: 1px;
        opacity: 0.8;
    }

    .pulse {
        width: 6px;
        height: 6px;
        background-color: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.5;
            transform: scale(1.5);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }

    .stats {
        margin-top: auto;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .stat {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
    }

    .stat .label {
        color: #888;
    }
    .stat .val {
        color: #fff;
    }

    .terminal {
        flex: 1;
        background: #000;
        border: 1px solid #111;
    }

    @media (max-width: 1024px) {
        .workspace {
            flex-direction: column;
        }
        .controls-panel {
            width: 100%;
        }
        .visual-panel,
        .terminal-panel {
            min-height: 300px;
        }
    }
</style>
