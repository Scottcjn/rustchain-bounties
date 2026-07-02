# Roadmap: Bug Bounty & Audit

## Objective
Identify and document security vulnerabilities, missing validations, and logical errors, focusing on "Low Hanging Fruits" within the `apps/api` and database interactions.

## Phases

### Phase 1: Reconnaissance (Audit)
- Analyze `apps/api/src/server.js` and route handlers.
- Map authentication and authorization flows (`jsonwebtoken` usage).
- Examine input validation coverage using `zod`.
- Audit `multer` configurations for insecure file upload vulnerabilities.
- Review rate limiting implementation.

### Phase 2: Vulnerability Assessment
- Document identified issues in `vulnerabilidades_encontradas.md`.
- Categorize by risk (High, Medium, Low).
- Propose mitigation strategies following SDD.

### Phase 3: Verification (SDD)
- Create `spec/features/[vulnerability-name]/spec.md` for prioritized issues.
- Develop `tasks.md` to fix and verify each issue with tests.
- Execute fixes atomistically, ensuring test passing.
