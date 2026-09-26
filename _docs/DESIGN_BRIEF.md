# Design Brief

## 1. Direction

KHOEBO is a calm, high-trust financial workspace: editorial typography and warm paper surfaces are balanced by an ink navigation and controlled coral actions. It should feel considered and local, not like a generic fintech template.

The interface is intentionally information-dense where customers work repeatedly: balances, transaction rows, order rows, payment forms, ATM actions, and proof details. Decorative cards are limited to framed tools and repeated records.

## 2. Look and feel

- Quiet, precise, and human.
- Warm paper background with a restrained green atmosphere.
- Dark ink for trust, contrast, and key balance panels.
- Coral for action and attention, not for every status.
- Green for positive balances and healthy service states.
- Thin borders, small uppercase labels, short clear verbs.
- No competitor logos, competitor names, or copied brand assets.

## 3. Palette

| Token | Value | Use |
| --- | --- | --- |
| `--ink` | `#15252A` | Primary text, dark panels, navigation |
| `--paper` | `#F5F4EF` | Page background |
| `--accent` | `#EE6C4D` | Primary actions, links, focus attention |
| `--mint` | `#BDD9C8` | Supporting green atmosphere |
| `--line` | `#D9DDD7` | Dividers and borders |
| Positive | `#32875B` | Credits, healthy, online |
| Soft green | `#E6EEE9` | Forms and secondary workspace panels |
| Soft coral | `#F1DFD5` | ATM/card attention and warnings |

## 4. Typography

- Display: Georgia/serif for human, editorial headings.
- Interface: Arial/sans-serif for labels, forms, status, data, and controls.
- Uppercase labels: 11-12px, strong letter spacing, muted color.
- Headings: responsive but constrained; never use hero-scale type inside compact controls.
- Body: 13-18px depending on context, with comfortable line height.
- Currency values: large serif numerals for balance emphasis; sans-serif for table values.

## 5. Components

- Top navigation: brand left, workspace links right, logout as a plain command button.
- Balance panel: dark ink, balance, account label, and masked account suffix.
- Summary tiles: four compact records for money in, money out, pockets, and rewards.
- Table panel: white framed work surface with thin row dividers and status columns.
- Transaction row: direction icon, description, category/date, amount, status.
- Action form: mint background, clear labels, grouped inputs, coral primary action.
- ATM console: dark terminal screen beside a service-selection rail.
- Proof sheet: white printable receipt with receipt number and key-value grid.
- Mobile preview: dark phone frame, quick-action row, activity list.

## 6. Screen layouts

- Dashboard: navigation, large balance, summary row, service cards, recent activity, capability strip.
- Banking: balance/control split, beneficiary and pocket CRUD panels, transfer form.
- Payments: balance/control split, payment form, history with Proof links.
- Transactions: focused table with activity rows and payment CTA.
- Trading: watchlist plus portfolio, order form, order lifecycle table.
- ATM center: terminal screen plus services; below it, action forms and activity.
- Proof: one printable sheet, minimal distractions, print action.
- Mobile preview: two-column desktop composition that collapses to phone then detail on mobile.
- Login: centered auth panel, sparse page, demo notice separated from credentials form.

## 7. Interaction and accessibility

- All mutations use explicit buttons and visible success/error messages.
- All forms need labels, CSRF, keyboard focus, and useful required constraints.
- Do not rely on color alone for credit/debit or status.
- Focus styles and error text must be visible in production polish pass.
- Mobile navigation should wrap without overlap.
- Print proof hides navigation and decorative UI.

## 8. Design acceptance criteria

- No table shows raw template markers or broken empty states.
- No button label overflows its parent at mobile width.
- ATM actions are visually distinct from informational terminal state.
- Proof is printable and legible in grayscale.
- Every screen preserves KHOEBO tokens and typography.
