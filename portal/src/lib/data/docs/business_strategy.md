# Corporate & Legal Strategy (Lineum)

This document serves as the master plan and summary for the future corporate and legal structuring of the Lineum project. It addresses Intellectual Property (IP) protection, inheritance, protection against external risks (e.g., software execution/asset seizure), and fair but secure equity distribution.

## 1. Inheritance and Minimizing Risk of State Forfeiture
The fundamental legal rule in the Czech Republic is that the state inherits property (escheat) only if there is no **last will and testament** and absolutely no legal heirs (relatives).
- **Notarial Will (Testament):** To ensure with certainty that the entirety of Lineum (including any corporate shares and finances) goes to Kateřina Marečková, a will must be drawn up by a notary. A notarial record is automatically saved in the central registry and cannot be lost or easily challenged.
- **Appointing a Substitute Heir:** To prevent the project from falling into the hands of the state even in extreme emergencies (e.g., if Kateřina cannot or will not accept the inheritance, or if an accident happens to both of you), you secure it with a **substitute heir**. You state in the will that if Kateřina does not inherit for any reason, the substitute will be, for example, Vlastimil Smeták, a specific close person, or an open-source foundation or university of your choice. This eliminates the state completely.

## 2. Intellectual Property (IP) Protection and Asset Seizure (Execution)
When an individual programs software, the copyright is logically divided into moral and economic rights.
- **Can an executor take Lineum?** Moral rights (the fact that you are the inventor/author) cannot be taken by anyone. However, an executor can seize **revenues** from economic rights (e.g., money you receive for commercial licenses) and your commercial shares in a company. The source code itself from your head or locked repositories is difficult for an executor to package into an auction, but they can legally block you from making money from it.
- **Primary Protection Strategy:** You should keep the ownership of the source code (Lineum Core) separate from the risk-bearing business. When you establish an LLC (s.r.o.) to operate the API portal, the company does not own the code; it merely holds an *exclusive commercial license* from you (the physical person). If the company is sued or goes bankrupt, Lineum does not fall with it. You simply terminate the license to the company and move on.

## 3. Corporate Structure and Equity
The Czech Corporations Act (ZOK) is highly flexible and allows you to set up absolute control. You can found the company as an **LLC (s.r.o.)** and, after gaining significant traction, transform it into a **Joint-Stock Company (a.s.)**. The rules can be fixed right away:

- **Founder's Share (Tomáš):** Will be defined with a vast majority of voting rights (e.g., veto power, or a voting weight of 100:1 compared to others) or simply a simple majority (e.g., 80+%). Therefore, even if you give away pieces of the company, you never lose the steering wheel.
- **Passive / Dividend Share (Kateřina):** To ensure her passive financial security (a share in profits and the sale of the company) while keeping the company protected, you issue her a *share without voting rights*. Major advantage: If anything bad happens (execution on her assets, disputes) and this share is officially acquired by a stranger, they gain money at most, but zero votes. No one gains the right to dictate your company.
- **Shareholders (Investors):** They receive minority shares with limited rights (e.g., right to information, but without the ability to change the company's direction without you).

## 4. Compensation for Vlastimil Smeták (Now vs. Future)
Avoid giving away a fixed portion of the company right at the beginning (the "founder's mistake"). The project is just starting its commercial phase.
- **What to give him now?** Public credit in publications and on The Scientist portal (already fulfilled – this holds immense global value for an academic) and a promise/partnership regarding exclusive publishing on OEA x Lineum cross-overs.
- **What for the future (MoU / ESOP):** Once the company is founded, you can sign a *Memorandum of Understanding* (MoU) or start a "vesting" schedule. This means: "Vlasto, you gain the right to, say, 2–5% of the company, and this share will be gradually assigned to you over the next 4 years (vesting), provided you continue to actively participate in the mathematical proofs of our core." This protects the company (if he stops working after half a year, he doesn't get a lifetime % of the company for free).

## 5. Further Critical Considerations

### A) Trademark "Lineum"
- Your Lineum code is protected by copyright and the AGPLv3 license, but **the word "Lineum" is not**.
- Commercial entities can (legally) take your code, but they cannot name it the same if you hold a trademark. This guarantees that **the only official Lineum** will always be yours.
- **Recommendation:** Submit a trademark registration application (at least for CZ/EU) for software services as soon as possible. It costs a few thousand CZK, but the brand value is incalculable.

### B) Digital Will and Access Rights (Escrow)
- A legal will dictates *who* owns it, but not *how* they access it.
- If the worst happens, Kateřina inherits the "copyrights," but practically cannot access your GitHub account, the `lineum.io` domain registry, or the portal hosting (Railway) without your passwords and 2FA codes.
- **Recommendation:** Set up a secure "Digital Vault" (e.g., via 1Password or an encrypted USB drive deposited with the notary alongside the will), containing the Master password to the project, 2FA recovery codes, and wallet keys, complete with clear instructions (a *Bus factor document*).

### C) LLC (s.r.o.) vs. Foundation (Non-profit Shield)
- World-class projects (Linux, OpenAI) often separate the creator from commerce via a foundation.
- **Future Recommendation (When Lineum is massive):** You can establish the Lineum Endowment Fund (Non-profit) and transfer the ownership of the Core code there. You appoint yourself as its lifetime head. A foundation cannot be executed like a physical person! Commercialization (SaaS API) is then handled by a separate, for-profit LLC/JSC that merely licenses data from the foundation. This creates an impenetrable shield between open-source science and hard market business risks.

## 6. Open Source (AGPLv3) vs. Commercial Ownership

It is a common misconception that "open source means it belongs to everyone and I lost control." This is categorically untrue.

### A) Copyright to the Equation and Code
- **Lineum is Open Source (AGPLv3), but it is NOT "Public Domain".**
- The copyright (Copyright © Tomáš Tříska) to both the equation and the *Lineum Core* source code belongs exclusively to you as a physical person at 100%.
- AGPLv3 is merely a **public licensing agreement** through which you (as the absolute owner) permit the world to study and use your code – **but only under your extremely strict conditions** (they must attribute you, they cannot secretly package it commercially, etc.).

### B) The Advantage of a Sole Owner (Dual-Licensing)
Because you are (according to `CITATION.cff` and `README.md`) the sole sovereign creator of the entire core:
- You offer the code to the world on GitHub with the "ball and chain" of AGPLv3 (which deters corporations from stealing it).
- **To Yourself (Your commercial LLC / Portal):** You can grant a commercial license *outside of AGPLv3*. As the author, you are not bound by your own open-source license! You write your company the commercial right to operate the API and portal.

### C) Execution Kill Switch in Practice
In the licensing agreement between you (the physical person/code owner) and your LLC (the portal operator), your lawyer will insert a **Change of Control** clause:
> *"In the event that the Licensor (Tomáš Tříska) loses majority control over the Licensee (Lineum s.r.o.) for any reason, or if an execution is levied upon the commercial share of the Licensee, this licensing agreement is automatically and immediately terminated, and all rights to use the software and API cease to exist."*

If an executor or a "hostile investor" arrives and seizes `Lineum s.r.o.`, that company instantly loses the right to even turn on the Portal and API (doing so would be theft of your software). The very next morning, you found a new company, `Lineum NextGen s.r.o.`, and pour the license into that.
