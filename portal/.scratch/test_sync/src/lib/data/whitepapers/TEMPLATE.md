**Title:** [Full Document Title]
**Document ID:** [lowercase-kebab-name]
**Document Type:** [Core | Hypothesis | Experiment | Extension]
**Version:** [x.y.z]
**Status:** [Draft | Locked | Retracted | Falsified]
**Date:** [YYYY-MM-DD]
---
# [Heading 1]

> [!WARNING]
> Include a relevant GitHub alert (WARNING, NOTE, IMPORTANT, TIP) here to provide context on the document's authority (e.g., "This is a working draft", or "This paper has been mathematically locked").

## 1. Abstract
*A concise summary of the theory, hypothesis, or core findings presented in this document.*

## 2. Introduction
*Background context and the specific problem or phenomenon this paper addresses within the Lineum architecture.*

## 3. Core Mechanics / Theory
*The detailed explanation of the proposed dynamics.*
* Ensure you reference `lineum-core.md` (Eq-4) if extending base mechanics.
* Use standard Markdown equations for mathematical consistency:
  $$ \nabla^2 \varphi = \dots $$

## 4. Evidence & Falsifiability
*How can this theory be proven or disproven?*
* What specific `TODO` sweeps, scripts, or metrics correspond to this hypothesis?

## 5. Conclusion
*Summary of implications.*

---
*(Note: If the `Status:` is updated to `Locked`, ensure the corresponding `audit_report.json` hash fingerprints are appended to the frontmatter.)*
