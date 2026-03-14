<script>
    import { onMount, tick, onDestroy, createEventDispatcher } from "svelte";
    import Chart from "chart.js/auto";
    import zoomPlugin from "chartjs-plugin-zoom";
    import { t } from "../i18n";

    const dispatch = createEventDispatcher();

    Chart.register(zoomPlugin);

    export let config = {};
    export let title = "";
    export let id = "chart-" + Math.random().toString(36).substr(2, 9);
    export let showMax = true;

    let canvas;
    let chart;

    $: if (config && chart) {
        chart.data = config.data;
        // Apply modifier logic to config options before update
        const finalConfig = applyZoomLogic(config);
        chart.options = finalConfig.options;
        chart.update("none");
    }

    function applyZoomLogic(cfg) {
        return {
            ...cfg,
            options: {
                ...cfg.options,
                plugins: {
                    ...cfg.options?.plugins,
                    zoom: {
                        ...cfg.options?.plugins?.zoom,
                        zoom: {
                            ...cfg.options?.plugins?.zoom?.zoom,
                            wheel: {
                                enabled: true,
                                modifierKey: "ctrl", // Only zoom when CTRL is pressed
                            },
                        },
                    },
                },
            },
        };
    }

    onMount(() => {
        const ctx = canvas.getContext("2d");
        const finalConfig = applyZoomLogic(config);
        chart = new Chart(ctx, finalConfig);
    });

    onDestroy(() => {
        if (chart) chart.destroy();
    });

    function handleMaximize() {
        dispatch("maximize", { title, config });
    }

    function resetZoom() {
        if (chart) chart.resetZoom();
    }

    let highlightZoomTips = false;
    let highlightTimeout;

    function handleWheel(e) {
        if (!e.ctrlKey) {
            highlightZoomTips = true;
            if (highlightTimeout) clearTimeout(highlightTimeout);
            highlightTimeout = setTimeout(() => {
                highlightZoomTips = false;
            }, 1500);
        }
    }
</script>

<div class="interactive-chart-wrapper" {id}>
    <div class="chart-header">
        <h3>{title}</h3>
        <div class="header-actions">
            {#if showMax}
                <button
                    type="button"
                    class="icon-btn"
                    on:click={handleMaximize}
                    aria-label="Maximize">{$t('chart_max')}</button
                >
            {/if}
            <button type="button" class="zoom-reset" on:click={resetZoom}
                >{$t('chart_reset')}</button
            >
        </div>
    </div>

    <div
        class="chart-container"
        role="img"
        aria-label={title}
        on:wheel={handleWheel}
    >
        <canvas bind:this={canvas}></canvas>
    </div>
    <p class="zoom-help" class:highlighted={highlightZoomTips}>
        <span class="ctrl-key">{$t('chart_ctrl')}</span> + {"Scroll to ZOOM" ||
            "Scroll to Zoom"}
    </p>
</div>

<style>
    .interactive-chart-wrapper {
        margin-bottom: 20px;
        position: relative;
    }

    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    h3 {
        font-size: 0.7rem;
        margin: 0;
        opacity: 0.8;
        border-left: 3px solid #ffaa00;
        padding-left: 10px;
        text-transform: uppercase;
        color: #00ffff;
    }

    .header-actions {
        display: flex;
        gap: 5px;
    }

    .icon-btn,
    .zoom-reset {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
        color: #00ffff;
        font-size: 0.6rem;
        padding: 2px 6px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .icon-btn:hover,
    .zoom-reset:hover {
        background: rgba(0, 255, 255, 0.3);
        border-color: #00ffff;
    }

    .chart-container {
        height: 200px;
        width: 100%;
        background: rgba(0, 0, 0, 0.2);
        cursor: grab;
    }

    .chart-container:active {
        cursor: grabbing;
    }

    .zoom-help {
        font-size: 0.6rem;
        opacity: 0.6;
        margin-top: 8px;
        color: #888;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 5px;
        transform-origin: left center;
    }

    .zoom-help.highlighted {
        opacity: 1;
        color: #ffaa00;
        transform: scale(1.05);
        font-weight: bold;
    }

    .ctrl-key {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 0.55rem;
        color: #fff;
    }

    .highlighted .ctrl-key {
        border-color: #ffaa00;
        background: rgba(255, 170, 0, 0.2);
        color: #ffaa00;
        box-shadow: 0 0 10px rgba(255, 170, 0, 0.5);
    }
</style>
