<script>
    export let isExpanded = false;
    export let title = "Collapsible Box";
    export let badgeText = "";
    export let badgeStyle = "background: #1f6feb; color: white;";
    export let containerStyle = "background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 20px;";
    export let headerStyle = "";
    export let contentStyle = "margin-top: 15px; border-top: 1px solid #30363d; padding-top: 15px;";
    export let testId = "";
</script>

<div
    class="collapsible-box"
    style="{containerStyle}"
>
    <div
        style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; {headerStyle}"
        on:click={() => (isExpanded = !isExpanded)}
        on:keydown={(e) => e.key === "Enter" && (isExpanded = !isExpanded)}
        role="button"
        tabindex="0"
        data-testid={testId}
    >
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
            <div style="flex: 1; display: flex; flex-direction: column;">
                <h4
                    style="margin: 0; font-size: 14px; display: flex; align-items: center; gap: 8px;"
                >
                    <span
                        style="font-size: 10px; color: #8b949e; display: inline-block; width: 12px; text-align: center;"
                    >
                        {isExpanded ? "▼" : "▶"}
                    </span>
                    {title}
                </h4>
                <!-- Slot for extra header content (e.g. counts) -->
                <slot name="header-meta" />
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px;">
                <slot name="header-actions" />
                {#if badgeText}
                    <span
                        style="font-size: 11px; padding: 2px 6px; border-radius: 12px; font-weight: bold; white-space: nowrap; {badgeStyle}"
                    >
                        {badgeText}
                    </span>
                {/if}
            </div>
        </div>
    </div>

    {#if isExpanded}
        <div style={contentStyle}>
            <slot />
        </div>
    {/if}
</div>
