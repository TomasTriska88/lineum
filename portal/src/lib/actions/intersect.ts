// Svelte Action: Calls the callback when node enters/leaves viewport
export function intersect(node: HTMLElement, callback: (inView: boolean) => void) {
    let observer: IntersectionObserver;

    const handleIntersect = (entries: IntersectionObserverEntry[]) => {
        entries.forEach(entry => {
            callback(entry.isIntersecting);
        });
    };

    if (typeof IntersectionObserver !== 'undefined') {
        observer = new IntersectionObserver(handleIntersect, { threshold: 0 });
        observer.observe(node);
    } else {
        // Fallback for SSR/JSDOM testing: assume it's visible
        callback(true);
    }

    return {
        update(newCallback: (inView: boolean) => void) {
            callback = newCallback;
        },
        destroy() {
            if (observer) {
                observer.disconnect();
            }
        }
    };
}
