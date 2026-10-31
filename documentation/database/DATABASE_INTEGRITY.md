# DATABASE_INTEGRITY.md — SolarFlow 360 Database Integrity & Concurrency Review

## 1. Relational Integrity & Referential Constraints
SolarFlow 360 enforces relational integrity at both the PostgreSQL engine level and Odoo ORM layer:

1. **Cascading Safety**:
   - Master reference data (`solar.system.type`) cannot be deleted if active installations or packages reference it (`ondelete='restrict'`).
   - Package BOM lines (`solar.package.line`) and Installation equipment lines (`solar.installation.line`) cascade with their parent header (`ondelete='cascade'`).
2. **Global Unique Constraints**:
   - `solar.system.type`: `UNIQUE(code)` enforced at database level.
   - `solar.installation.line`: Serial number uniqueness enforced across active installations to prevent duplicate equipment allocation.
   - `solar.warranty`: Unique sequence generation `WRN/%(year)s/XXXX` without gaps.

---

## 2. Concurrency Control & Race Condition Mitigation

1. **Simultaneous Equipment Reservation**:
   - Serial number allocation uses Odoo ORM transactional atomic commits. If two technicians attempt to scan or allocate the same inverter serial number concurrently, the second transaction is rolled back with a `ValidationError`.
2. **Concurrent Installation State Updates**:
   - State transitions (`action_start_testing`, `action_customer_signoff`, `action_commission`) require specific prior states. Concurrent updates trigger optimistic locking or rollback to prevent skipped testing stages.
3. **Transaction Rollback Testing**:
   - Verified that if commissioning fails (e.g., missing inverter serial number), the installation remains in `completed` state and no orphaned warranty records are created in `solar.warranty`.

---

## 3. Data Cleansing & Deduplication Rules

- **Customer Matching**: Duplicate detection inspects `phone`, `mobile`, and `email_from` across `crm.lead` and `res.partner`.
- **Orphan Prevention**: Surveys, Installations, Warranties, and Service Tickets are strictly bound to a valid `partner_id`.

