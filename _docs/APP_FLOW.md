# Application Flow and Screen Specification

## 1. Entry and onboarding

### Login screen

URL: `/login/`

- Shows KHOEBO identity, username, password, and secure-demo notice.
- **Sign in:** authenticates and redirects to `/`.
- **Invalid credentials:** stays on login and shows an error.
- **Authenticated user visiting login:** should be redirected to the dashboard in production.
- Current demo access: `demo` / `KHOEBO2026!`.

Planned onboarding: identity details, cellphone verification, password creation, device registration, consent, product selection, and first-login security setup.

## 2. Authenticated navigation

The workspace navigation contains Dashboard, Transactions, Payments, Mobile, ATM, and Logout. The ATM item is intentionally between Mobile and Logout.

## 3. Screen inventory

| Screen | Route | Main actions | Success | Error |
| --- | --- | --- | --- | --- |
| Dashboard | `/` | View balance, summaries, recent transactions, open services | Data renders | Login redirect or data error |
| Transactions | `/transactions/` | Review all activity, open payments | Rows render with status | Empty state |
| Payments | `/payments/` | Create payment, open proof | Payment and proof reference created | Invalid amount or missing fields |
| Proof of payment | `/payments/{id}/proof/` | View and print receipt | Printable receipt | Unauthorized or missing payment |
| Banking | `/banking/` | Add/remove beneficiary, create/remove pocket, submit transfer | Record appears with message | Invalid target or validation error |
| Mobile preview | `/mobile/` | Review mobile client direction | Feature preview | N/A |
| ATM redirect | `/atm/` | Enter default terminal | Redirects to `/atm/center/042/` | Login redirect |
| ATM center | `/atm/center/{terminal_id}/` | Withdraw, deposit, send cash, receive cash, review activity | Cash record and transaction created | Invalid amount or unavailable terminal |
| Rewards | `/rewards/` | Earn points, redeem points, edit/delete ledger entries | Points balance and ledger update | Invalid points or insufficient redemption balance |
| Trading | `/trading/` | Add/remove watchlist, create order, open edit | Record appears with status | Invalid instrument or order data |
| Edit order | `/trading/orders/{id}/edit/` | Change side, quantity, limit | Updated order | Unauthorized/missing order |
| Capability map | `/capabilities/` | Explore product areas and try demo actions | HTMX confirmation | Login redirect |
| Bills | `/bills/` | Create, mark paid, delete bills | Bill status updates | Invalid amount/date |
| Invoices | `/invoices/` | Create and delete invoices | Invoice register updates | Missing recipient or amount |
| Profile | `/profile/` | Update customer details | Profile saved | Invalid email/input |
| Notifications | `/notifications/` | Mark all read, delete notification | Read state or row removed | Unauthorized notification |
| Settings | `/settings/*/` | Manage security, payment methods, API access, activity | Setting or record updates | Invalid setting |
| Lock / OTP / reset | `/lock/`, `/otp/`, `/reset/` | Lock session, verify, start reset | Security flow continues | Failed or expired verification |

## 4. ATM center flow

1. User selects **ATM** in navigation.
2. `/atm/` redirects to `/atm/center/042/`.
3. Terminal screen shows location, online state, cash units, cardless, and contactless state, with four selector keys on both sides.
4. User selects withdrawal, deposit, cash send, cash receive, balance, mini statement, or card services.
5. Money movement asks the user to select an account, enter/choose an amount, and enter a recipient or voucher reference where required.
6. A review screen shows service, account, amount, and recipient/reference; side keys can edit details, cancel, or approve.
7. Only approval writes a `CashTransfer`, matching `Transaction`, and unique `ATMReceipt`.
8. User receives a printable, owner-scoped receipt and the terminal activity list updates.

## 5. Payment and proof flow

1. User opens Payments.
2. User enters beneficiary, amount, and reference.
3. Django creates `Payment`, `Transaction`, and `ProofOfPayment`.
4. User sees a success message containing the receipt number.
5. User selects **Proof** in payment history.
6. Receipt shows amount, beneficiary, reference, status, date, and print action.

## 6. Trading journey

1. User opens Trading.
2. Seeded instruments and watchlist appear.
3. User adds/removes instruments.
4. User selects instrument, side, quantity, and limit price.
5. User queues the order.
6. User edits or cancels the order from the order list.
7. Production execution would move the order through risk, execution, settlement, and reporting states.

## 7. Button/action contract

- `Sign in`: POST `/login/`.
- `Log out`: POST `/logout/` with CSRF token.
- `View all`: GET `/transactions/`.
- `Make a payment`: GET `/payments/`.
- `Submit payment`: POST `/payments/`.
- `Proof`: GET `/payments/{id}/proof/`.
- `Print proof`: browser print action.
- `Add beneficiary`: POST `/banking/` with `action=create_beneficiary`.
- `Edit beneficiary`: GET/POST `/banking/beneficiaries/{id}/edit/`.
- `Remove beneficiary`: POST `/banking/beneficiaries/{id}/delete/`.
- `Create pocket`: POST `/banking/` with `action=create_pocket`.
- `Edit pocket`: GET/POST `/banking/pockets/{id}/edit/`.
- `Remove pocket`: POST `/banking/pockets/{id}/delete/`.
- `Rewards`: POST `/rewards/` to earn/redeem; GET/POST `/rewards/{id}/edit/`; POST `/rewards/{id}/delete/`.
- `ATM side keys`: POST `/atm/center/{id}/` with service/account/amount/edit/cancel/help commands.
- `ATM amount and recipient forms`: POST `/atm/center/{id}/` with `command=amount` or `command=recipient`.
- `Approve ATM action`: POST `/atm/center/{id}/` with `command=approve` after review.
- `Cancel ATM flow`: POST `/atm/center/{id}/` with `command=cancel`; no cash record is created.
- `ATM receipt`: GET `/atm/receipts/{transfer-id}/` after approval.
- `Add watchlist`: POST `/trading/` with `action=add_watchlist`.
- `Queue order`: POST `/trading/` with `action=create_order`.
- `Edit order`: GET/POST `/trading/orders/{id}/edit/`.
- `Cancel order`: POST `/trading/orders/{id}/delete/`.

## 8. Testing journeys

- Anonymous user requests `/transactions/`, `/payments/`, `/banking/`, `/trading/`, and `/atm/`: each redirects to login.
- Demo login redirects to dashboard and seeds idempotent instruments and pockets.
- Payment submission creates a payment, transaction, and proof.
- ATM route redirects to terminal 042; cash actions remain uncommitted until approval, then create a movement, ledger transaction, and receipt.
- Trading CRUD creates, updates, and cancels an order.
- User A cannot access User B's payment, proof, beneficiary, pocket, ATM record, or order.
- Empty states show only when querysets are empty; no template marker is visible.
