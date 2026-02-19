import { writable } from 'svelte/store';

export const hudActive = writable(true); // AI is always present
export const isChatOpen = writable(false); // Controls expansion
