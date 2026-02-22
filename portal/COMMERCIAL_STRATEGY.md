# Lineum Commercial & API Strategy

## 1. The "Open-Core" Business Model
Lineum operates on a dual-layer strategy:
- **Core Technology (Open Source):** The underlying mathematical engine (Continuous Field Dynamics, Tensor calculations) is open and accessible. This builds academic trust, peer review, and community adoption.
- **Enterprise API Solutions (Proprietary / Paid):** The production-ready infrastructure built on top of the core.

### Why Companies Pay for the API:
1. **Infrastructure & Scaling:** Running massively parallel tensor fields requires specialized DevOps, auto-scaling clusters, and memory handling. The API abstracts this into a single HTTP request.
2. **SLA & Reliability:** B2B clients demand 99.9% uptime and dedicated support (Service Level Agreements). An open-source repository provides zero guarantees.
3. **Time-to-Market:** Integrating the API takes 3 lines of code (e.g., in JavaScript or Python). Building custom cloud infrastructure around the open-source core takes months of engineering hours.
4. **Proprietary Wrappers:** The API layer provides "Secret Sauce" features not found in the math core: geographical API bindings (GeoJSON/Mapbox), intelligent route caching, specific formatting, and hardware optimization.

## 2. General Purpose Framework
**CRITICAL:** Routing is currently the primary showcase, but **Lineum is a generalized physical solver.**
The architecture and marketing portal must always reflect that Routing is simply the *first* application. Future endpoints will include:
- Structural stress testing
- Fluid dynamics & aerodynamic bounding
- Supply chain equilibrium (economic fields)

*Marketing Rule:* Always present "Lineum API Solutions" as a growing suite of tools, where "Swarm Routing" is just one active module.

## 3. The Dual-Revenue Model: Enterprise API + Open-Source Donations
While the primary revenue engine is the Enterprise API, **Open-Source Donations (e.g., GitHub Sponsors, Patreon, BuyMeACoffee) are highly recommended.** 

### Why Donations and Paid APIs are not mutually exclusive:
1. **Audience Separation:** 
   - *Donations* come from individual academic researchers, students, and indie developers who love the math and use the open-source repository locally.
   - *API Payments* come from B2B Corporations (Logistics, Manufacturing) who need SLA guarantees and cloud infrastructure. A corporation will not use "Donations" to secure their production infrastructure; they require a legal API contract.
2. **Community Goodwill:** Having a prominent "Support the Open-Source Core" button next to the "Buy API Key" button reinforces the Open-Core philosophy. It shows corporations that they are funding a beloved academic project, which acts as positive PR.
   
*Implementation Rule:* The UI should strictly separate these calls to action. The main portal Header should focus on the API (B2B), while the GitHub README and the Portal Footer/Wiki should feature the Donation links heavily (B2C/Academic).

## 4. Legal & Terms of Service (ToS) Requirements
Before full public API launch, the following must be legally drafted by counsel:
1. **API Usage Limits & Rate Limiting:** Clear definitions of mathematical complexity limits per API call to prevent computationally bankrupting the server.
2. **Data Privacy (GDPR/CCPA):** Defining whether Floorplans, Grid Matrices, and logistical data sent to the API are stored for model training or immediately flushed from RAM.
3. **SLA Definitions:** Explicitly defining what constitutes downtime.
4. **License Distinction & Architectural Boundaries (Open-Core):** 
   - **Open Source Math Engine (AGPLv3):** The `lineum` core mathematical codebase will be explicitly licensed under the **GNU Affero General Public License v3 (AGPLv3)**. This preserves auditability and scientific integrity while preventing "wrapper-reselling."
   - *Why AGPLv3?* AGPL dictates that anyone offering the engine as a network-facing service must release their source code if they modify the AGPL code or tightly couple it. Separate auxiliary services (billing, frontend) can remain proprietary only if there is a strict architectural boundary.
   - **Proprietary SaaS Layer (`lineum-portal` / `lineum-saas`):** The orchestration, API gateway, authentication, billing, and scaling mechanics are completely separate. While you (Tomáš Tříska) are the sole Copyright holder and have dual-licensing rights, we will enforce a strict API/Process separation where the SaaS wrapper only calls the AGPL core engine as a remote service. This guarantees zero license contamination and proves the proprietary code is an independent orchestrator, not a derivative work.

5. **Intellectual Property (Trademarks & Patents):**
   - **Trademarks (Lineum™):** The brand name "Lineum", the logo, and the portal design are distinct from the open-source code. We must begin using the ™ symbol (e.g., Lineum™ API Solutions) across the portal to establish "common law" trademark rights. Once revenue begins, a formal registered trademark (®) should be filed in target jurisdictions (EUIPO/USPTO) to prevent competitors from confusing the market.
   - **Patents:** While abstract mathematical formulas (Eq-4) are generally not patentable, the *specific application* of Continuous Field Dynamics to *scalable network routing* via parallel tensor hardware can be patented as a "Software/Hardware Apparatus". If patenting is a long-term goal, a provisional patent application should be filed *before* making the repository fully public, to secure the priority date.

## 4. Marketing Tone
- **Confident, not defensive:** We don't hide that the math is free. We celebrate it. *"The math is open. The millisecond-reliability is guaranteed by our cloud."*
- **Developer-Centric:** Speak to engineers. Show them code snippets. They are the ones who will convince their CTOs to buy the API instead of building it.
- **Relentlessly Highlight Competitive Advantages:** Always visually prioritize features and metrics that traditional discrete algorithms (like A* or Dijkstra) cannot physically achieve. Massive concurrent scaling O(1), sub-millisecond continuous tensor evaluations, and complete elimination of graph bottlenecking must be the central, unmissable focal points of any product showcase.
