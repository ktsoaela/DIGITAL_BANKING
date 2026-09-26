# Database Schema

## 1. Ownership rule

Each service owns its database. The Django web database contains the current authenticated demo workspace and user-facing ledger. FastAPI services have separate SQLite files and must not read the Django database directly.

## 2. Web database

### Django framework tables

| Table | Important fields | Relationships |
| --- | --- | --- |
| `auth_user` | `id`, `username`, password hash, names, active flags, timestamps | Owns all user records |
| `django_session` | session key, session data, expiry | Authenticated browser sessions |
| `django_content_type` | app/model metadata | Migration/admin support |
| `auth_group`, `auth_permission`, joins | role and permission metadata | Planned staff authorization |

### Product tables

| Table | Fields and types | Relationships |
| --- | --- | --- |
| `dashboard_transaction` | `id bigint`, `user_id FK`, `description varchar(140)`, `category varchar(60)`, `amount decimal(12,2)`, `direction varchar(6)`, `status varchar(30)`, `created_at datetime` | User has many transactions |
| `dashboard_payment` | `id bigint`, `user_id FK`, `beneficiary varchar(120)`, `amount decimal(12,2)`, `reference varchar(140)`, `status varchar(30)`, `created_at datetime` | User has many payments |
| `dashboard_proofofpayment` | `id bigint`, `user_id FK`, `payment_id one-to-one`, `receipt_number varchar(40)`, `created_at datetime` | One proof per payment |
| `dashboard_beneficiary` | `id bigint`, `user_id FK`, `name varchar(120)`, `account_identifier varchar(80)`, `bank_label varchar(80)`, `created_at datetime` | User has many beneficiaries |
| `dashboard_pocket` | `id bigint`, `user_id FK`, `name varchar(60)`, `target_amount decimal(12,2)`, `balance decimal(12,2)`, `rate decimal(5,2)`, `created_at datetime` | User has many pockets |
| `dashboard_instrument` | `id bigint`, `symbol varchar(12) unique`, `name varchar(120)`, `price decimal(12,2)`, `day_change decimal(6,2)`, `currency varchar(3)` | Shared market catalogue |
| `dashboard_watchlistitem` | `id bigint`, `user_id FK`, `instrument_id FK`, `created_at datetime` | Unique user/instrument constraint |
| `dashboard_tradeorder` | `id bigint`, `user_id FK`, `instrument_id FK`, `side varchar(4)`, `quantity positive int`, `limit_price decimal(12,2)`, `status varchar(30)`, `created_at datetime` | User order belongs to instrument |
| `dashboard_atmterminal` | `terminal_id varchar(20) PK`, `location varchar(120)`, `status varchar(30)`, `cash_units varchar(120)`, `contactless bool`, `cardless bool` | Referenced by cash transfers |
| `dashboard_cashtransfer` | `id bigint`, `user_id FK`, `terminal_id nullable FK`, `account_label varchar(80)`, `direction varchar(10)`, `amount decimal(12,2)`, `recipient varchar(120)`, `reference varchar(80)`, `status varchar(30)`, `created_at datetime` | User cash movement at optional terminal; created only after approval |
| `dashboard_atmreceipt` | `id bigint`, `transfer_id one-to-one FK`, `receipt_number unique`, `created_at datetime` | Printable proof for an approved ATM movement |
| `dashboard_bill` | `id bigint`, `user_id FK`, `payee varchar(120)`, `amount decimal(12,2)`, `due_date date`, `status varchar(30)`, `created_at datetime` | User bill register |
| `dashboard_invoice` | `id bigint`, `user_id FK`, `invoice_number unique`, `name`, `bill_to`, `amount decimal(12,2)`, issue/due dates, status | User invoice register |
| `dashboard_paymentmethod` | `id bigint`, `user_id FK`, `label`, `kind`, `masked_identifier`, `is_default`, `created_at` | User payment instruments; sensitive values must remain masked |
| `dashboard_notification` | `id bigint`, `user_id FK`, `title`, `body`, `kind`, `is_read`, `created_at` | User notification inbox |
| `dashboard_apikey` | `id bigint`, `user_id FK`, `name`, `key_prefix`, `status`, `last_used_at`, `created_at` | User API access metadata; full secrets are not stored |
| `dashboard_customerprofile` | `id bigint`, `user_id one-to-one`, phone, country, verification, 2FA, alerts, locked | Customer profile and security flags |
| `dashboard_rewardentry` | `id bigint`, `user_id FK`, action (`earn`, `redeem`, `adjust`), points, description, status, `created_at` | User rewards ledger; redeem entries reduce available points |

## 3. FastAPI SQLite tables

### Banka API: `banka.sqlite3`

- `transfers(id, account_id, amount, reference)`
- `feature_events(id, event_type, payload)`

Current feature events support instant payments and savings-pocket API records. Production should normalize these into account, ledger, beneficiary, payment, idempotency, and audit tables.

### ATM API: `atm.sqlite3`

- `withdrawals(id, card_token, amount, terminal_id)`
- `atm_events(id, event_type, payload)`

Production should add terminal inventory, cardless vouchers, cash deposit batches, receipts, reversals, and settlement records.

### Trading API: `trading.sqlite3`

- `orders(id, account_id, symbol, side, quantity)`
- `forex_events(id, event_type, payload)`

Production should add quotes, instruments, portfolios, positions, orders, executions, FX wallets, conversions, BOP declarations, evidence, limits, and audit events.

## 4. Data rules

- All currency amounts use `decimal(12,2)` in the web schema.
- Every customer-owned table includes a user/account owner.
- Delete operations must be scoped by owner; no object is deleted by primary key alone.
- Instrument deletion is protected when orders reference it.
- Payment proofs are one-to-one with payments and have unique receipt numbers.
- Production databases require created/updated timestamps, audit actor, correlation ID, idempotency key, and immutable ledger entries.

## 5. Future production schema changes

- Replace SQLite with PostgreSQL-compatible types and constraints.
- Introduce a double-entry ledger rather than calculating balances from display transactions.
- Separate PII, payment instrument data, and operational data.
- Add encryption/key references for sensitive fields.
- Add retention and anonymization policies.
