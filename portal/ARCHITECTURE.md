# Lineum Portal: Architecture Overview

This document describes the technical architecture of the Lineum Portal, its components, and infrastructure.

## 🏗 High-Level Architecture

The project is divided into three main layers that together form the Lineum ecosystem.

```mermaid
    User((User)) --> ZT[Cloudflare Access / Zero Trust]
    ZT --> CF[Cloudflare DNS / Proxy]
    CF --> Frontend[SvelteKit Frontend / Portal]
    Frontend --> API[Python API Engine]
    Frontend --> CMS[Directus CMS]
    API --> CMS
    API --> DB[(DB / Data Storage)]
    API --> Workers[Background Generators]
    
    subgraph "Infrastructure (Railway.app)"
        Frontend
        API
        CMS
        Workers
    end
```

## 🛠 Tech Stack

### 1. Frontend: Lineum Portal & Lab
- **Framework:** [SvelteKit](https://kit.svelte.dev/)
- **Language:** TypeScript
- **Key Features:**
  - **Portal:** Main entry point, documentation, and presentation.
  - **Lab:** Interactive laboratory environment for simulations and analysis (utilizes Three.js and Chart.js).
- **Deployment:** Automated build on Railway.app on every push to `main`.

### 2. Backend: API & Processing
- **Language:** Python 3.x
- **Key Components:**
  - **Lineum Core Engine:** The mathematical and simulation core of the project.
  - **FastAPI / Flask:** (Planned) To serve the paid API.
  - **Background Generators:** Continuous 24/7 processes generating data for simulations and the API.

### 3. CMS & Data Management: Directus
- **Platform:** [Directus](https://directus.io/) (Headless CMS)
- **Role:** Centralized data management, content for the Portal, and administrative interface for simulations.
- **Hosting:** Self-hosted on Railway.app (Docker-based).

### 4. Infrastructure (Hosting)
- **Platform:** [Railway.app](https://railway.app)
  - **Model:** PaaS (Platform as a Service) – zero server management.
  - **Scaling:** Usage-based (billing based on actual CPU and RAM consumption).
- **DNS & Domain:** [Cloudflare](https://www.cloudflare.com/)
  - **Domain:** `lineum.io`
  - **Security:** SSL, DDoS protection, and speed optimization via Cloudflare Proxy.

## 🌿 Git Workflow & Branching

To maintain stability and enable automated deployments, we use a structured branching strategy:

- **`main` Branch:**
  - **Purpose:** Production-ready code and stable releases.
  - **Deployment:** Automatically triggers deployment to the production environment on Railway.app.
  - **Access:** Only merged from `dev` after verification.
- **`dev` Branch:**
  - **Purpose:** Primary working branch for active development and hypothesis testing.
  - **Sync:** All new features and lab experiments are committed here first.
- **Workflow:**
  1. Development happens on `dev`.
  2. Once a milestone is reached and tested, `dev` is merged into `main`.
  3. Merge to `main` triggers the live infrastructure update.

## 🚀 Automation & Deployment

Deployment is handled collaboratively via **GitHub Actions**:
- **Verification:** Every change undergoes testing.
- **Approval:** Production deployment can require manual confirmation by the user.
- **Transparency:** Infrastructure configuration is stored as code (`railway.json` / workflow files).

## 📖 Living Document Policy

This document is a **Living Document**. It MUST be updated whenever:
- New infrastructure components are added or modified.
- Deployment automation (CI/CD) workflows are established or changed.
- Domain or security settings (DNS, SSL, Cloudflare) are updated.
- Significant architectural shifts occur in the Portal or Lab.

Both the user and the AI assistant are responsible for keeping this overview in sync with the actual state of the repository.

## 🔒 Security & Access Control

During the Alpha/Development phase, access is restricted using **Cloudflare Zero Trust (Access)**:
- **Authentication:** Users must verify their identity via a **One-Time Pin (OTP)** sent to their authorized email address.
- **Authorized Users:**
  - Jiri Hernik
  - Tomas Triska
  - Vlastimil Smetak
- **Scope:** The entire domain `lineum.io` is protected, blocking unauthorized access to the Portal, Lab, and Directus CMS.

---
*Last update: February 16, 2026*
