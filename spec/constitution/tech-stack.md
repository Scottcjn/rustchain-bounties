# Technical Stack: Freelance Platform Monorepo

## Overview
A monorepo structure containing a backend API, a frontend application, and shared packages.

## Core Stack
- **Runtime:** Node.js (ES Modules)
- **Framework:** Express.js
- **Language:** JavaScript (Node.js) / TypeScript (based on conventions, need to verify if `.ts` files exist)
- **Validation:** Zod
- **Security:**
  - `cors`
  - `express-rate-limit`
  - `helmet`
  - `jsonwebtoken`
- **File Upload:** `multer`
- **Database:** (To be determined via `packages/db`)

## Project Structure
- `apps/api`: Express.js backend.
- `apps/web`: Frontend application.
- `packages/db`: Likely database access layer.
- `packages/ui`: Shared UI components.
