
import { marked } from "marked";
import markedKatex from "marked-katex-extension";
import "katex/dist/katex.min.css";

const options = {
    throwOnError: false,
    nonStandard: true // Enable $...$ syntax
};

marked.use(markedKatex(options));

export { marked };
