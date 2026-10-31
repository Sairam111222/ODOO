# AGENTS.md — Permanent Engineering Instructions

## 1. Project Context
- **Product Name**: SolarFlow 360
- **Organization**: SunPower Solutions
- **Target Scale**: ~40 residential & small commercial rooftop installations / month
- **Workforce**: 15 Field Technicians, Site Surveyors, Sales Crew, Support Agents, Accounting, Leadership
- **Core Technology**: Odoo 17 Community Edition (Python, PostgreSQL 15, XML, OWL/JS) deployed via Docker Compose

## 2. Engineering Principles & Directives
1. **Never Bypass Odoo ORM**: All business data access must leverage the standard Odoo ORM. No rogue direct SQL injections or ad-hoc CRUD backends.
2. **Preserve Odoo CE Boundaries**:
   - `industry_fsm` (Field Service) and `planning` are Odoo Enterprise. We model field technician operations in `solar_installation` extending native `project.task` and custom scheduling.
   - `account_accountant` is Enterprise. Basic invoicing is provided by CE `account`. Financial reporting logic must remain standard CE compliant.
3. **Security by Default**:
   - UI hiding is not security. Every sensitive transition must be protected via server-side `@api.model` / `@api.depends` validation and proper group permissions.
   - Record rules (`ir.rule`) must strictly constrain Technicians to their own assigned jobs and Surveyors to their assigned surveys.
4. **No Destructive Operations**: Never drop tables or delete production data without explicit user confirmation.
5. **Code Style & Conventions**:
   - Model names: snake_case with dots (e.g., `solar.site.survey`).
   - Field names: snake_case (e.g., `recommended_capacity_kw`).
   - XML IDs: module_prefixed descriptive names (e.g., `view_solar_site_survey_form`).
   - Manifests must declare all XML and CSV files in `data` in exact dependency order (security first, data second, views third).
6. **Documentation Integrity**: Maintain `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, and `SECURITY_CHECKLIST.md` updated as implementation progresses.

