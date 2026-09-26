# KHOEBO_DIGITAL_BANKING

A service-oriented digital banking platform for the Khotso product family.

## Service map

| Service | Responsibility | Runtime | Port |
| --- | --- | --- | --- |
| `banka-web` | Customer web experience and HTMX dashboard | Django 6 | 8000 |
| `banka-api` | Accounts, balances, and banking transactions | FastAPI | 8001 |
| `digital-banking-api` | ATM operations and cash access | FastAPI | 8002 |
| `khoebo-api` | Trading instruments and orders | FastAPI | 8003 |
| `banka-app` | Mobile client | Flutter (existing project) | - |

Each backend owns its SQLite database. Services communicate over HTTP and expose a small health endpoint for orchestration.

## Run locally

```powershell
cd KHOEBO_DIGITAL_BANKING
docker compose up --build
```

Open the dashboard at http://localhost:8000. Sign in at `/login/` with the development demo account `demo` / `KHOEBO2026!`. From there, use the protected banking workspace:

- http://localhost:8000/banking/ for balances and transfers
- http://localhost:8000/atm/ for ATM withdrawal preparation
- http://localhost:8000/trading/ for watchlists and order preparation
- http://localhost:8000/transactions/ for transaction history
- http://localhost:8000/payments/ for payment creation and payment history
- http://localhost:8000/payments/<payment-id>/proof/ for a printable proof of payment
- http://localhost:8000/mobile/ for the mobile banking experience preview
- http://localhost:8000/atm/center/042/ for the live ATM center
- http://localhost:8000/capabilities/ for the complete KHOEBO feature map

API documentation is available at `/docs` on ports 8001-8003. These web workflows are demo interactions; they return an HTMX confirmation and do not move real money until authentication, authorization, and API calls are connected.

## KHOEBO capability scope

- **Internet banking:** accounts, statements, CSV/PDF/OFX exports, beneficiaries, scheduled and bulk payments, debit-order controls, tax and civic payment records, and a security centre.
- **Mobile banking:** biometric approvals, card freeze/unfreeze/replacement, virtual cards, cellphone-based instant payments, low-data access, QR/tap payments, airtime/data/electricity vouchers, and fraud reporting.
- **Savings and value:** named savings pockets, target tracking, eligible positive-balance returns, overdraft visibility, KHOEBO rewards, and included protection details.
- **Forex and offshore:** multi-currency wallets, rate watchlists, currency conversion, travel money, offshore order preparation, allowance tracking, and BOP declarations with supporting-document review.
- **ATM and self-service:** cardless vouchers, cash deposits, contactless access, second-factor approval, receipts/statements, PIN changes, and replacement-card requests.

The API contracts for these capabilities live under `/v1/payments`, `/v1/pockets`, `/v1/cards`, `/v1/cardless-withdrawals`, `/v1/deposits`, `/v1/forex`, and `/v1/orders`. Restart API processes after source changes so they load the latest routes.

### Local Python run

If Docker Desktop is not running, start the services in four terminals:

```powershell
cd KHOEBO_DIGITAL_BANKING\services\web
python manage.py migrate
python manage.py runserver 127.0.0.1:8010
```

```powershell
cd KHOEBO_DIGITAL_BANKING\services\banka-api
python -m uvicorn app.main:app --port 8001
```

Use the same command from `services\atm-api` on port `8002` and `services\trading-api` on port `8003`.

## Development notes

- Django is pinned to the Django 6.x line for the 2026 platform baseline.
- HTMX is used for server-rendered interactions in the web dashboard.
- FastAPI owns domain APIs; Django owns the web experience and session/UI concerns.
- The existing Flutter client remains in `banka/banka_app` and should consume `banka-api` and the ATM/trading APIs through an environment-specific API base URL.
- The new Flutter client starter lives in `KHOEBO_DIGITAL_BANKING/mobile` and mirrors the protected web workspace with overview, activity, services, payments, forex, ATM, and security entry points.
- This is a foundation, not a production banking deployment. Add authentication, authorization, audit events, encryption, rate limiting, secrets management, and observability before handling real money.
