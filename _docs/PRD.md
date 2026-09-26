# Product Requirements Document

## 1. Product overview

KHOEBO DIGITAL BANKING is a locally governed digital banking platform for everyday money movement, savings, payments, cash access, global money, and investing. It combines a secure Django/HTMX web workspace, FastAPI domain services, a Flutter mobile client, and an ATM service boundary.

The product goal is one account story across every channel: a customer can sign in, understand their money, pay, save, move cash, access ATM services, manage cards, prepare forex activity, and review financial activity from web, mobile, or a terminal.

## 2. Product principles

- Clarity before complexity: show balance, status, cost, and next action.
- Local-first: use ZAR as the default currency and support local cellphone payments, cash services, and exchange-control workflows.
- One customer story: web, mobile, APIs, and ATM actions use consistent concepts and references.
- Secure by default: sensitive actions need authentication, authorization, auditability, and step-up controls.
- Honest state: demo actions are labelled as demo; production settlement is never implied.

## 3. Users

- Personal customer: checks balances, pays, saves, sends or receives cash, and manages cards.
- Investor: watches instruments, creates or cancels orders, manages forex wallets, and prepares offshore activity.
- ATM customer: performs withdrawal, deposit, cardless, receipt, and card-service actions.
- Support or operations user: investigates events, disputes, failures, and audit records. Planned.
- Compliance user: reviews BOP declarations, identity evidence, limits, and suspicious activity. Planned.

## 4. Core capabilities

### Identity and access

- Login and logout are implemented for the development demo.
- Seeded demo account: `demo` / `KHOEBO2026!`.
- Protected web routes redirect unauthenticated users to login.
- Planned: registration, password recovery, MFA, biometrics, device binding, identity verification, roles, and session risk controls.

### Web and internet banking

- Dashboard balance, income, spending, savings, rewards, and recent transactions.
- Transaction history with category, amount, direction, status, and timestamp.
- Payment creation and payment history.
- Beneficiary create, read, update, and delete.
- Savings pocket create, read, update, and delete.
- Rewards ledger create, read, update, and delete, with earn/redeem balance validation.
- Proof-of-payment creation and printable viewing.
- Planned: payment edit/cancel, recurring payments, bulk files, statements, exports, debit-order controls, and approvals.

### Mobile banking

- Flutter client starter in `mobile/`.
- Overview, activity, services, payments, forex, ATM, cards, and security entry points.
- Environment-based API direction is documented.
- Planned: actual API client, secure token storage, platform biometrics, push notifications, offline-safe read cache, and device registration.

### ATM and cash

- Dynamic live terminal route: `/atm/center/042/`.
- Seeded terminal state, online status, cash units, cardless and contactless indicators.
- Withdrawal, cash send, cash receive, and deposit actions persist cash records and transactions.
- ATM activity history.
- Planned: real terminal protocol, PIN/PAN security, note validation, cash inventory, reversals, settlement, and hardware integration.

### Trading and forex

- Seeded instruments and watchlist.
- Watchlist add/remove.
- Trade order create, edit, and cancel.
- Instrument price and daily movement display.
- FastAPI contracts for markets, orders, forex wallets, conversions, and BOP declarations.
- Planned: market-data provider, suitability checks, execution, settlement, allowance validation, BOP evidence, tax reporting, and portfolio valuation.

### Value and control

- Capability map for web, mobile, forex, ATM, savings, credit, rewards, and protection.
- Chelete-derived account tools: bills, invoices, profile, notifications, payment methods, API access, security settings, lock, OTP, and reset entry points.
- Planned: rewards ledger, policy records, overdraft lifecycle, card controls, fraud centre, and support case management.

## 5. Non-functional requirements

- Responsive at mobile, tablet, and desktop widths.
- WCAG 2.2 AA target for production UI.
- All money values use decimal arithmetic and explicit currency.
- All user-owned records are filtered by authenticated user.
- Mutations use CSRF protection on Django forms and authorization checks.
- Every financial mutation must have an audit event in production.
- Health checks must be available for each service.
- APIs must provide stable versioned contracts under `/v1/`.

## 6. Success measures

- 95% of seeded demo journeys complete without an error.
- Login-to-balance view in under 3 seconds on local production-like infrastructure.
- 100% of payment, cash, and order mutations have a visible status and reference.
- 0 cross-user data leaks in authorization tests.
- 100% of critical paths covered by automated tests before production readiness.

## 7. Acceptance criteria

The current development milestone is accepted when a user can log in, view the dashboard, create a beneficiary, create a savings pocket, create a payment, view its proof, open ATM center 042, perform four cash actions, view transactions, open trading, manage a watchlist, and create/edit/cancel an order using seeded data.
