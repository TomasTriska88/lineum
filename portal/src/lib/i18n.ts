import { createI18n } from "@inlang/paraglide-sveltekit";
import * as runtime from "$lib/paraglide/runtime.js";

export const pathnames = {
    "/api-solutions": {
        en: "/api-solutions",
        cs: "/api-reseni",
        de: "/api-loesungen",
        ja: "/api-solutions"
    },
    "/support": {
        en: "/support",
        cs: "/podpora",
        de: "/support",
        ja: "/support"
    },
    "/wiki": {
        en: "/wiki",
        cs: "/znalostni-baze",
        de: "/wissensdatenbank",
        ja: "/wiki"
    },
    "/about": {
        en: "/about",
        cs: "/o-nas",
        de: "/ueber-uns",
        ja: "/about"
    }
} as const;

export const i18n = createI18n(runtime, {
    defaultLanguageTag: "en",
    pathnames
});
