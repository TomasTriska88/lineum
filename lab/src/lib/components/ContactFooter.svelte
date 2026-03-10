<script lang="ts">
    // @ts-ignore
    import pkg from "../../../../package.json";
    
    // @ts-ignore
    const commitHash =
        typeof __GIT_HASH__ !== "undefined" ? __GIT_HASH__ : "dev";
</script>

<div class="status-bar" aria-label="System Status" translate="no">
    <!-- Left Section: Branding & Open Source Status -->
    <div class="status-group left">
        <span class="status-item brand" title="Lineum Laboratory Environment">LINEUM LAB</span>
        <span class="status-item text-dim hide-mobile" title="Open Source License">AGPLv3</span>
    </div>

    <!-- Center Section: Procedural Warning -->
    <div class="status-group center hide-mobile">
        <span class="status-item warning-text" title="The Laboratory is a sandbox for visualizing preliminary results of partially verified hypotheses. It is for exploratory verification of phenomena that must be subsequently confirmed via official whitepaper outputs.">
            <span class="pulse-dot"></span>
            PROCEDURAL WARNING: SANDBOX
        </span>
    </div>

    <!-- Right Section: Technical Meta & Links -->
    <div class="status-group right">
        <!-- Optional: Future space for background sync status, websocket status, etc. -->
        <span class="status-item text-dim" title="Current Build Hash">
            <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3zm0 0V9zm0 0a3 3 0 0 0-3-3v12a3 3 0 0 0 3 3m-6-6v6a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V9a3 3 0 0 1 3-3h3v12"/></svg>
            {commitHash}
        </span>
        <span class="status-item text-dim hide-mobile" title="System Version">
            v{pkg.version}
        </span>
        <a
            href="https://github.com/TomasTriska88/lineum-private"
            target="_blank"
            rel="noopener noreferrer"
            class="status-item link highlight"
            title="Repository"
        >
            GitHub
        </a>
    </div>
</div>

<style>
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 24px; /* Professional IDE Status Bar height */
        background: #000000; /* Absolute black / solid for the base boundary */
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: stretch;
        font-family: var(--font-mono, "Consolas", monospace);
        font-size: 0.65rem;
        color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.5);
    }

    .status-group {
        display: flex;
        align-items: stretch;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 0 10px;
        transition: background-color 0.15s ease, color 0.15s ease;
        border-right: 1px solid rgba(255, 255, 255, 0.05); /* subtle dividers */
        cursor: default;
    }

    .status-group.right .status-item {
        border-right: none;
        border-left: 1px solid rgba(255, 255, 255, 0.05);
    }

    .status-item.brand {
        color: #fff;
        font-weight: 600;
        letter-spacing: 0.05em;
        background: rgba(255, 255, 255, 0.05);
    }

    .warning-text {
        color: rgba(255, 100, 100, 0.85);
        font-weight: 600;
        letter-spacing: 0.08em;
        cursor: help;
        background: rgba(255, 50, 50, 0.05);
    }

    .warning-text:hover {
        background: rgba(255, 50, 50, 0.15);
        color: #ffb3b3;
    }

    .pulse-dot {
        width: 6px;
        height: 6px;
        background-color: #ff3b30;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 6px #ff3b30;
        animation: pulse 2s infinite ease-in-out;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
    }

    .text-dim {
        color: rgba(255, 255, 255, 0.4);
    }
    
    .status-item:not(.link):hover {
        background: rgba(255, 255, 255, 0.08);
        color: rgba(255, 255, 255, 0.8);
    }

    .icon {
        opacity: 0.7;
        margin-right: 2px;
    }

    .link {
        color: inherit;
        text-decoration: none;
        cursor: pointer;
    }

    .link:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
    }

    .link.highlight {
        color: rgba(0, 255, 255, 0.7);
    }

    .link.highlight:hover {
        color: #00ffff;
        background: rgba(0, 255, 255, 0.1);
    }

    @media (max-width: 600px) {
        .hide-mobile {
            display: none;
        }
        .status-item {
            padding: 0 6px;
        }
    }
</style>
