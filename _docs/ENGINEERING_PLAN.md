# Engineering Plan

## 1. Goal

Deliver a secure, testable KHOEBO digital banking platform with a coherent web experience, Flutter client, banking APIs, ATM services, and trading/forex services.

## 2. Team model

| Role | Responsibility |
| --- | --- |
| Product owner | Priorities, acceptance, customer outcomes |
| UX/UI designer | Flows, accessibility, responsive visual system |
| Django engineer | Auth, web workspace, ORM, templates, admin/support tools |
| API engineers | Banka, ATM, trading contracts and domain rules |
| Flutter engineer | Mobile screens, secure storage, device capabilities |
| QA/security engineer | Test plans, authorization, threat modeling, release gates |
| Platform engineer | Containers, CI/CD, secrets, observability, backups |

## 3. Build order

### Phase 0: foundation, complete

- Establish monorepo service map.
- Add Docker Compose and health checks.
- Add Django/HTMX web shell.
- Add FastAPI banking, ATM, and trading boundaries.
- Add isolated SQLite databases.

### Phase 1: customer workspace, complete for development

- Add Django login/logout and protected routes.
- Add seeded demo user and ledger transactions.
- Add payments, proofs, transactions, beneficiaries, and pockets.
- Add trading watchlist and order CRUD.
- Add dynamic ATM center 042 and cash actions.
- Add Flutter mobile starter.

### Phase 2: correctness and security

- Add automated authorization tests for every user-owned model.
- Add idempotency keys and immutable audit events.
- Add proper balance/ledger service and transaction boundaries.
- Add MFA, device binding, password recovery, and rate limiting.
- Add input validation and consistent API error envelopes.
- Replace demo secret and credentials.

### Phase 3: financial integrations

- Integrate payment provider and local instant-payment rail.
- Integrate ATM switch or terminal simulator.
- Integrate market data and order execution provider.
- Add FX rates, multi-currency wallet settlement, and BOP review.
- Add identity, KYC/AML, sanctions, and fraud decisioning.

### Phase 4: production operations

- Move databases to managed PostgreSQL or service-appropriate stores.
- Add TLS, reverse proxy, workers, backups, monitoring, traces, and alerts.
- Add CI builds, migrations, image scanning, dependency updates, and disaster recovery tests.
- Run independent penetration, privacy, and compliance reviews.

## 4. Small testable tasks

1. Add login success and invalid-login tests.
2. Add anonymous redirect tests for every protected route.
3. Add user-isolation tests for payment, proof, pocket, beneficiary, cash, and order records.
4. Add payment creates transaction and proof test.
5. Add proof print HTML smoke test.
6. Add ATM 042 redirect and terminal seed test.
7. Add withdrawal, deposit, cash-send, and cash-receive persistence tests.
8. Add order create/edit/cancel tests.
9. Add watchlist uniqueness test.
10. Add empty-state template tests.
11. Add FastAPI health and OpenAPI checks.
12. Add API validation tests for invalid amounts and quantities.
13. Add Compose config and image build in CI.
14. Add Flutter analyze and widget smoke test when Flutter is available.

## 5. Dependencies

- Python 3.13.
- Django 6.x target for the container baseline.
- FastAPI and Uvicorn.
- SQLite for development; PostgreSQL target for production.
- Docker Desktop for Compose execution.
- Flutter SDK 3.x for mobile development.
- Optional production integrations: payment rail, ATM switch, FX/market data, KYC/AML, secrets manager, observability platform.

## 6. Acceptance criteria

### Product

- A new user can understand balance, activity, payments, savings, ATM, mobile, forex, and trading paths.
- Demo user can complete all current seeded journeys without manual database editing.
- Payment proof is created and printable.
- ATM 042 supports all four current cash movements.
- Trading supports watchlist and order lifecycle CRUD.

### Engineering

- `python manage.py check` passes.
- All migrations apply from an empty database.
- Critical Django journeys pass automated tests.
- API health endpoints return 200.
- Compose config validates and image builds in CI.
- No user-owned object can be read or mutated by another user.
- No development credential or secret reaches production configuration.

## 7. Timeline

| Sprint | Focus | Exit metric |
| --- | --- | --- |
| 1 | Foundation and current web workspace | Compose config and Django checks green |
| 2 | Auth, ledger, payments, proof | Login/payment/proof journey green |
| 3 | ATM center and cash services | Four ATM actions persist and display references |
| 4 | Trading/forex workflows | Watchlist and order lifecycle green |
| 5 | Flutter API integration | Mobile overview reads a real API in emulator |
| 6 | Security and authorization | No cross-user access in automated suite |
| 7 | Integrations and compliance | Provider sandbox journeys green |
| 8 | Production readiness | Restore, monitoring, scan, and release gates green |

## 8. Metrics

- Authentication success rate and failed-login rate.
- Payment completion, rejection, and proof-generation rate.
- ATM action success rate by terminal and action.
- Trading order validation, acceptance, cancellation, and execution rates.
- API p95 latency and error rate.
- Percentage of critical journeys covered by automated tests.
- Number of authorization findings and unresolved security issues.
- Mobile crash-free sessions and API availability.
