/**
 * Svelte action to move an element to the document body.
 * Useful for modals and tooltips to breakout of overflow: hidden or z-index constraints.
 */
export function portal(node: HTMLElement) {
    let target = document.body;
    target.appendChild(node);
    return {
        destroy() {
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        }
    };
}
