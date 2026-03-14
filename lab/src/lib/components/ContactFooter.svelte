<script lang="ts">
    import { t } from '../i18n.js';
    import pkg from '../../../../portal/package.json';
    // @ts-ignore
    const commitHash =
        typeof __GIT_HASH__ !== "undefined" ? __GIT_HASH__ : "dev";
    
    const activeVersion = pkg.version;
</script>

<div class="status-bar" aria-label="System Status" translate="no">
    <!-- Left Section: Branding & Open Source Status -->
    <div class="status-group left">
        <span class="status-item brand" data-tooltip="Lineum Laboratory Environment">{$t('lab_brand')}</span>
        <span class="status-item text-dim hide-mobile" data-tooltip="Open Source License">{$t('license_agpl')}</span>
    </div>

    <!-- Center Section: Procedural Warning -->
    <div class="status-group center hide-mobile">
        <span class="status-item warning-text" data-tooltip={$t('sandbox_warning')}>
            <span class="pulse-dot"></span>
            {$t('procedural_warning')}
        </span>
    </div>

    <!-- Right Section: Technical Meta & Links -->
    <div class="status-group right">
        <!-- Optional: Future space for background sync status, websocket status, etc. -->
        <span class="status-item text-dim" data-tooltip={$t('current_build_hash')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3zm0 0V9zm0 0a3 3 0 0 0-3-3v12a3 3 0 0 0 3 3m-6-6v6a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V9a3 3 0 0 1 3-3h3v12"/></svg>
            v{activeVersion}
        </span>
        <span class="status-item text-dim hide-mobile" data-tooltip={$t('system_version')}>
            {commitHash}
        </span>
        <a
            href="https://github.com/TomasTriska88/lineum-private"
            target="_blank"
            rel="noopener noreferrer"
            class="status-item link highlight"
            data-tooltip={$t('repository_link')}
        >
            {$t('repo_github')}
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
        padding: 0 10px; /* pridal margin, aby LINEUM LAB nebyl uplne nalepeny na levo */
    }

    .status-group {
        display: flex;
        align-items: stretch;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 0 12px;
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

    /* Custom Tooltip Styling */
    [data-tooltip] {
        position: relative;
    }
    
    [data-tooltip]::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 150%;
        left: 50%;
        transform: translateX(-50%);
        background: #161b22;
        color: #c9d1d9;
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid #30363d;
        font-family: var(--font-mono, "Consolas", monospace);
        font-size: 11px;
        font-weight: normal;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.2s ease, visibility 0.2s ease;
        pointer-events: none;
        z-index: 10000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    [data-tooltip]:hover::after {
        opacity: 1;
        visibility: visible;
    }

    /* Handle screen edges so tooltip doesn't overflow */
    .status-group.left [data-tooltip]::after {
        left: 0;
        transform: none;
    }
    .status-group.right [data-tooltip]::after {
        left: auto;
        right: 0;
        transform: none;
    }
</style>
