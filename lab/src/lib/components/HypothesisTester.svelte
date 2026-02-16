<script>
    import { onMount } from "svelte";
    import Chart from "chart.js/auto";
    import zoomPlugin from "chartjs-plugin-zoom";
    import { t } from "../i18n";

    Chart.register(zoomPlugin);

    export let dataRoot = "";

    let discoveryData = null;
    let fourierCanvas;
    let riemannCanvas;
    let fourierChart;
    let riemannChart;

    $: if (dataRoot) {
        loadDiscovery();
    }

    async function loadDiscovery() {
        try {
            const res = await fetch(
                `${dataRoot}/discovery.json?t=${Date.now()}`,
            );
            discoveryData = await res.json();
            renderCharts();
        } catch (e) {
            console.error("Failed to load discovery data", e);
        }
    }

    function renderCharts() {
        if (!discoveryData) return;
        renderFourier();
        renderRiemann();
    }

    function renderFourier() {
        if (!fourierCanvas) return;
        if (fourierChart) fourierChart.destroy();

        const ctx = fourierCanvas.getContext("2d");
        fourierChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: discoveryData.fourier_spectrum.map((_, i) =>
                    (i / 100).toFixed(2),
                ),
                datasets: [
                    {
                        label: $t("chart_label_fourier"),
                        data: discoveryData.fourier_spectrum,
                        borderColor: "#ffaa00",
                        backgroundColor: "rgba(255, 170, 0, 0.2)",
                        tension: 0.4,
                        pointRadius: 0,
                        borderWidth: 2,
                    },
                    {
                        label: $t("chart_ghost_chaos"),
                        data: discoveryData.fourier_spectrum.map(
                            () => Math.random() * 2,
                        ),
                        borderColor: "rgba(0, 255, 255, 0.1)",
                        borderDash: [5, 5],
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: "index" },
                plugins: {
                    legend: { display: false },
                    zoom: {
                        zoom: {
                            wheel: { enabled: true },
                            pinch: { enabled: true },
                            mode: "x",
                        },
                        pan: { enabled: true, mode: "x" },
                    },
                },
                scales: {
                    x: {
                        grid: { color: "rgba(0, 255, 255, 0.1)" },
                        ticks: { color: "#00ffff", font: { size: 10 } },
                        title: {
                            display: true,
                            text: $t("chart_label_component"),
                            color: "#00ffff",
                        },
                    },
                    y: {
                        grid: { color: "rgba(0, 255, 255, 0.1)" },
                        ticks: { color: "#00ffff" },
                        title: {
                            display: true,
                            text: $t("chart_label_amplitude"),
                            color: "#00ffff",
                        },
                    },
                },
            },
        });
    }

    function renderRiemann() {
        if (!riemannCanvas) return;
        if (riemannChart) riemannChart.destroy();

        const ctx = riemannCanvas.getContext("2d");
        riemannChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: discoveryData.norm_riemann.map((_, i) => i),
                datasets: [
                    {
                        label: $t("chart_ghost_order"),
                        data: discoveryData.norm_riemann.map(
                            (_, i) =>
                                i / (discoveryData.norm_riemann.length - 1),
                        ),
                        borderColor: "rgba(0, 255, 0, 0.2)",
                        borderDash: [10, 5],
                        borderWidth: 1,
                        pointRadius: 0,
                    },
                    {
                        label: $t("chart_label_riemann"),
                        data: discoveryData.norm_riemann,
                        borderColor: "#cc0000",
                        backgroundColor: "transparent",
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.2,
                    },
                    {
                        label: $t("chart_label_dejavu"),
                        data: discoveryData.norm_dejavu,
                        borderColor: "#ffaa00",
                        backgroundColor: "#ffaa00",
                        borderWidth: 2,
                        pointRadius: 4,
                        tension: 0.2,
                        showLine: true,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: "index" },
                plugins: {
                    legend: {
                        labels: {
                            color: "#00ffff",
                            boxWidth: 12,
                            font: { size: 9 },
                        },
                    },
                    zoom: {
                        zoom: {
                            wheel: { enabled: true },
                            pinch: { enabled: true },
                            mode: "xy",
                        },
                        pan: { enabled: true, mode: "xy" },
                    },
                },
                scales: {
                    x: {
                        grid: { color: "rgba(0, 255, 255, 0.1)" },
                        ticks: { color: "#00ffff", font: { size: 9 } },
                        title: {
                            display: true,
                            text: $t("chart_label_index"),
                            color: "#00ffff",
                        },
                    },
                    y: {
                        min: -0.1,
                        max: 1.1,
                        grid: { color: "rgba(0, 255, 255, 0.1)" },
                        ticks: { color: "#00ffff" },
                        title: {
                            display: true,
                            text: $t("chart_label_normalized"),
                            color: "#00ffff",
                        },
                    },
                },
            },
        });
    }

    onMount(() => {
        if (dataRoot) loadDiscovery();
    });
</script>

<div class="hypothesis-tester">
    <div class="panel-header">
        <div class="panel-title">{$t("discovery_analysis")}</div>
    </div>

    <div class="insight-cards">
        <div class="insight-card">
            <div class="card-icon">🧩</div>
            <div class="card-content">
                <strong
                    >LINEUM LEGO-UNIVERSE <span class="data-badge"
                        >{$t("data_source")}</span
                    ></strong
                >
                <p>{$t("insight_lego_universe")}</p>
            </div>
        </div>
        <div
            class="insight-card highlight"
            class:visible={discoveryData?.pearson_r > 0.9}
        >
            <div class="card-icon">⚡</div>
            <div class="card-content">
                <strong
                    >THE PRIME BEAT <span class="data-badge"
                        >{$t("data_source")}</span
                    ></strong
                >
                <p>{$t("insight_riemann_meaning")}</p>
            </div>
        </div>
    </div>

    <div class="discovery-metrics">
        <div class="metric">
            <span class="label">{$t("pearson_correlation")}</span>
            <span class="value" class:high={discoveryData?.pearson_r > 0.9}>
                {discoveryData?.pearson_r
                    ? (discoveryData.pearson_r * 100).toFixed(2) + "%"
                    : "0.00%"}
            </span>
        </div>
        <div class="metric">
            <span class="label">{$t("structure_stability")}</span>
            <span class="value">
                {discoveryData?.euclidean_dist
                    ? ((1 / (1 + discoveryData.euclidean_dist)) * 100).toFixed(
                          1,
                      ) + "%"
                    : "0.0%"}
            </span>
        </div>
        <div class="metric">
            <span class="label">{$t("field_turbulence")}</span>
            <span class="value">
                {discoveryData?.euclidean_dist?.toFixed(3) || "0.000"}
            </span>
        </div>
    </div>

    <div class="chart-section">
        <div class="chart-header">
            <h3>{$t("fourier_title")}</h3>
            <button class="zoom-reset" on:click={() => fourierChart.resetZoom()}
                >RESET ZOOM</button
            >
        </div>
        <div class="chart-container">
            <canvas bind:this={fourierCanvas}></canvas>
        </div>
        <p class="chart-tip">{$t("zoom_tip")}</p>
    </div>

    <div class="chart-section">
        <div class="chart-header">
            <h3>{$t("riemann_title")}</h3>
            <button class="zoom-reset" on:click={() => riemannChart.resetZoom()}
                >RESET ZOOM</button
            >
        </div>
        <div class="chart-container">
            <canvas bind:this={riemannCanvas}></canvas>
        </div>
        <p class="chart-tip">{$t("zoom_tip")}</p>
    </div>
</div>

<style>
    .hypothesis-tester {
        padding: 15px;
        background: rgba(0, 20, 20, 0.5);
        border: 1px solid rgba(0, 255, 255, 0.2);
        color: #00ffff;
        font-family: "Courier New", Courier, monospace;
    }

    .panel-header {
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(0, 255, 255, 0.3);
        padding-bottom: 10px;
    }

    .panel-title {
        font-size: 0.9rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: bold;
    }

    .insight-cards {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 25px;
    }

    .insight-card {
        display: flex;
        gap: 15px;
        background: rgba(0, 255, 255, 0.05);
        padding: 12px;
        border-radius: 4px;
        border-right: 2px solid rgba(0, 255, 255, 0.2);
    }

    .insight-card.highlight {
        display: none;
        background: rgba(0, 255, 0, 0.05);
        border-right-color: #00ff00;
        animation: glow 3s infinite alternate;
    }

    .insight-card.highlight.visible {
        display: flex;
    }

    .card-icon {
        font-size: 1.5rem;
    }

    .card-content strong {
        display: block;
        font-size: 0.7rem;
        letter-spacing: 1px;
        margin-bottom: 4px;
        color: #ffaa00;
    }

    .card-content p {
        margin: 0;
        font-size: 0.75rem;
        line-height: 1.4;
        opacity: 0.9;
    }

    @keyframes glow {
        from {
            box-shadow: 0 0 5px rgba(0, 255, 0, 0.1);
        }
        to {
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
        }
    }

    .discovery-metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-bottom: 25px;
        background: rgba(0, 255, 255, 0.05);
        padding: 10px;
        border-radius: 4px;
    }

    .metric {
        display: flex;
        flex-direction: column;
    }

    .metric .label {
        font-size: 0.6rem;
        opacity: 0.7;
        margin-bottom: 4px;
    }

    .metric .value {
        font-size: 1.1rem;
        font-weight: bold;
        color: #fff;
    }

    .metric .value.high {
        color: #00ff00;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
    }

    .chart-section {
        margin-bottom: 30px;
        position: relative;
    }

    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .zoom-reset {
        background: rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
        color: #00ffff;
        font-size: 0.6rem;
        padding: 2px 6px;
        cursor: pointer;
    }

    .zoom-reset:hover {
        background: rgba(0, 255, 255, 0.2);
    }

    h3 {
        font-size: 0.7rem;
        margin: 0;
        opacity: 0.8;
        border-left: 3px solid #ffaa00;
        padding-left: 10px;
    }

    .chart-container {
        height: 200px;
        width: 100%;
        background: rgba(0, 0, 0, 0.2);
        cursor: crosshair;
    }

    .chart-tip {
        font-size: 0.6rem;
        opacity: 0.5;
        margin-top: 5px;
        font-style: italic;
    }
</style>
