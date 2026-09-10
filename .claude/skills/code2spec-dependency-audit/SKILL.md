---
name: code2spec-dependency-audit
metadata:
  code-skills:
    id: code2spec/code2spec-dependency-audit
description: "Analyzes internal libraries (SOUP) and external service dependencies (APIs, Databases, Cloud) to map system architecture, evaluate security/maintenance risks, and generate visual context diagrams."
---

# Skill: Dependency & External Audit (SOUP)

## Objective

Identify all external elements the system relies on—including Software of Unknown Provenance (SOUP)—and assess their impact on the system's security, stability, and maintainability.

## Instructions

### 1. Multi-Source Discovery

Scan beyond manifest files to identify the full dependency footprint:

- **Application Layer:** Analyze `package.json`, `pnpm-lock.yaml`, `requirements.txt`, `go.mod`, `build.gradle`, `build.gradle.kts`, `Podfile`, `Package.swift`, or `Package.resolved` to extract core libraries and their versions.
- **Environment & Service Layer:** Review `.env.example`, `docker-compose.yml`, `next.config.js`, `init-db.sql`, or `google-services.json` to detect integrations with external services (e.g., Auth providers, OpenAI API, Stripe, Vector DBs, Firebase, Google Play Services).

### 2. Role-Based Mapping

Categorize identified dependencies to define their functional role within the architecture:

- **Core Frameworks:** (e.g., Next.js, Tailwind CSS, FastAPI)
- **Data & State Management:** (e.g., Prisma ORM, Tanstack Query, Redis, Pinecone)
- **External Infrastructure & APIs:** (e.g., AWS S3, Clerk Auth, LLM Providers, Payment Gateways)

### 3. SOUP Risk Evaluation

Evaluate each major external dependency based on the following risk factors:

- **Maintainability:** Check for "dead" libraries (no updates in >1 year) or low community activity.
- **Security & Vulnerabilities:** Identify known CVEs or high-severity security alerts (e.g., via `npm audit` logic).
- **Criticality (SPOF):** Determine if the dependency is a Single Point of Failure. What happens to the system if this specific API or library goes down?

### 4. Visualization Requirement

- Generate a **Mermaid System Context Diagram**.
- Represent the **Core Application** as the central node.
- Use directional arrows to show data flow and dependencies toward **External Services**, **Databases**, and **Infrastructure Providers**.

## Constraints

- **Privacy:** Do NOT include actual API keys or sensitive credentials; use placeholder variable names only.
- **Insight-First:** Prioritize actionable insights (e.g., "Version upgrade recommended" or "High-risk dependency detected") over a simple list of names.
