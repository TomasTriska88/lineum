import { createI18n } from "@inlang/paraglide-sveltekit";
import * as runtime from "$lib/paraglide/runtime.js";

export const i18n = createI18n(runtime, {
    defaultLanguageTag: "en",
    pathnames: {
        "/api-solutions": {
            en: "/api-solutions",
            cs: "/api-reseni",
            de: "/api-loesungen",
            ja: "/api-solutions"
        },
        "/about": {
            en: "/about",
            cs: "/o-nas",
            de: "/ueber-uns",
            ja: "/about"
        }
    }
});
