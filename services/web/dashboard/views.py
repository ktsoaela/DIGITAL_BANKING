from datetime import date, timedelta
import csv
from decimal import Decimal, InvalidOperation
import secrets
from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from django.utils import timezone

from .models import APIKey, ATMReceipt, ATMTerminal, BankAccount, BankCard, Beneficiary, Bill, CashTransfer, CustomerProfile, DebitOrder, Instrument, Invoice, Notification, Payment, PaymentMethod, PaymentRequest, Pocket, PocketMovement, ProofOfPayment, RewardEntry, ServicePurchase, TradeOrder, Transaction, WatchlistItem

REWARD_EDIT_TEMPLATE = "dashboard/reward_edit.html"
SETTINGS_TEMPLATE = "dashboard/settings.html"
REWARD_ACTIONS = {RewardEntry.EARN, RewardEntry.REDEEM, RewardEntry.ADJUST}
ATM_BACK_LABEL = "Back to services"


SERVICES = [
    {"name": "Internet banking", "slug": "banka-api", "purpose": "Accounts, payments, savings, and statements", "port": 8001},
    {"name": "Mobile banking", "slug": "banka-app", "purpose": "Secure everyday banking from your phone", "port": 8001},
    {"name": "ATM network", "slug": "digital-banking-api", "purpose": "Cash access, deposits, and self-service", "port": 8002},
    {"name": "Forex & trading", "slug": "khoebo-api", "purpose": "Currencies, offshore investing, and orders", "port": 8003},
]


CAPABILITY_GROUPS = [
    {
        "key": "web",
        "eyebrow": "01 / WEB & INTERNET BANKING",
        "title": "The control centre.",
        "intro": "A high-trust desktop workspace for the actions that benefit from a larger screen and a clear audit trail.",
        "features": [
            ("Accounts & statements", "Balances, beneficiaries, transaction history, and downloadable CSV, PDF, or OFX records."),
            ("Payments & approvals", "Single payments, bulk payment files, scheduled transfers, future-dated orders, and approval rules."),
            ("Debit order control", "Review, pause, dispute, and track debit orders before they leave the account."),
            ("Tax & civic payments", "A guided payment workspace for tax and civic services with a saved receipt trail."),
            ("Security centre", "Sign-in alerts, trusted devices, transaction limits, fraud reporting, and profile lock."),
        ],
    },
    {
        "key": "mobile",
        "eyebrow": "02 / MOBILE BANKING",
        "title": "Banking in your pocket.",
        "intro": "Fast, low-data actions for the moments between places, with device biometrics and instant controls.",
        "features": [
            ("Biometric approvals", "Fingerprint or face verification for sign-in and high-risk actions, backed by step-up security."),
            ("Card controls", "Freeze, unfreeze, replace, set limits, and create virtual cards without waiting for support."),
            ("Instant cellphone payments", "Send money to a cellphone number or payment alias and track the recipient status."),
            ("Everyday value-added services", "Buy airtime, data, electricity, entertainment vouchers, and other local services."),
            ("QR and tap payments", "Scan supported payment codes, use contactless cards, and connect a digital wallet."),
        ],
    },
    {
        "key": "forex",
        "eyebrow": "03 / FOREX & OFFSHORE",
        "title": "Global money, locally governed.",
        "intro": "A dedicated KHOEBO workspace for currencies, travel, offshore investing, and compliant international receipts.",
        "features": [
            ("Multi-currency wallets", "Hold and exchange USD, GBP, EUR, AUD, and additional supported currencies."),
            ("Automated BOP declarations", "Capture the purpose and supporting information for incoming international funds before release."),
            ("Offshore investing", "Create global share orders, monitor allowance usage, and keep a complete exchange-control record."),
            ("Travel money", "Fund a virtual or physical multi-currency card and manage travel spending limits."),
            ("Rate watchlists", "Set target exchange rates and receive a prompt before converting your money."),
        ],
    },
    {
        "key": "atm",
        "eyebrow": "04 / ATM & SELF-SERVICE",
        "title": "More than cash.",
        "intro": "Paperless ATM and foyer services that connect the physical network to the KHOEBO account experience.",
        "features": [
            ("Cardless cash", "Withdraw a secure cash voucher sent from web or mobile without inserting a physical card."),
            ("Cash deposits", "Deposit validated notes and receive an immediate digital receipt and balance update."),
            ("Tap and biometric access", "Start a session with contactless access and approve sensitive actions with a second factor."),
            ("Statements and receipts", "Print or send an official statement, transaction receipt, or proof of payment."),
            ("Card services", "Replace a lost card, update a PIN, and manage delivery from a self-service terminal."),
        ],
    },
    {
        "key": "money",
        "eyebrow": "05 / SAVINGS, CREDIT & REWARDS",
        "title": "Make the everyday work harder.",
        "intro": "Simple money tools that help customers separate goals, understand costs, and earn value from normal activity.",
        "features": [
            ("Savings pockets", "Create linked pockets for goals, bills, and emergencies with names, targets, and rules."),
            ("Positive-balance returns", "Show applicable rates and projected returns for eligible savings pockets."),
            ("Overdraft access", "Display eligibility, limit, pricing, usage, and repayment clearly before activation."),
            ("KHOEBO rewards", "Earn points from qualifying activity and exchange them for cash, vouchers, or fee benefits."),
            ("Included protection", "Surface eligible accidental or funeral cover, policy details, beneficiaries, and claims support."),
        ],
    },
]


@require_GET
def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    transactions = Transaction.objects.filter(user=request.user)[:5]
    total_credits = Transaction.objects.filter(user=request.user, direction=Transaction.CREDIT).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    total_debits = Transaction.objects.filter(user=request.user, direction=Transaction.DEBIT).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    accounts = BankAccount.objects.filter(user=request.user)
    active_accounts = accounts.filter(status=BankAccount.ACTIVE)
    first_account = accounts.first()
    pockets = request.user.pockets.all()
    context = {"services": SERVICES, "capability_groups": CAPABILITY_GROUPS, "transactions": transactions, "credits": total_credits, "debits": total_debits, "accounts": accounts, "primary_account": first_account, "available_total": sum((account.balance for account in active_accounts), Decimal("0.00")), "pockets": pockets, "pocket_total": sum((pocket.balance for pocket in pockets), Decimal("0.00")), "points_balance": _reward_balance(request.user)}
    return render(request, "dashboard/index.html", context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    demo_user, created = User.objects.get_or_create(username="demo", defaults={"first_name": "KHOEBO", "last_name": "Demo"})
    if created:
        demo_user.set_password("KHOEBO2026!")
        demo_user.save(update_fields=["password"])
        Transaction.objects.bulk_create([
            Transaction(user=demo_user, description="Salary received", category="Income", amount=Decimal("18500.00"), direction=Transaction.CREDIT),
            Transaction(user=demo_user, description="Card purchase", category="Everyday", amount=Decimal("420.00"), direction=Transaction.DEBIT),
            Transaction(user=demo_user, description="Monthly account fee", category="Banking", amount=Decimal("69.00"), direction=Transaction.DEBIT),
            Transaction(user=demo_user, description="Savings pocket transfer", category="Savings", amount=Decimal("1200.00"), direction=Transaction.DEBIT),
        ])
    _seed_demo_data(demo_user)
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""), password=request.POST.get("password", ""))
        if user is not None:
            login(request, user)
            return redirect("home")
        messages.error(request, "Those sign-in details were not recognised.")
    return render(request, "dashboard/login.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@require_GET
@login_required
def capabilities(request):
    return render(request, "dashboard/capabilities.html", {"capability_groups": CAPABILITY_GROUPS})


@require_http_methods(["GET", "POST"])
@login_required
def banking(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_beneficiary":
            Beneficiary.objects.create(user=request.user, name=request.POST.get("name", ""), account_identifier=request.POST.get("account_identifier", ""))
            messages.success(request, "Beneficiary added to your account.")
        elif action == "create_pocket":
            try:
                target_amount = Decimal(request.POST.get("target_amount", "0"))
                if target_amount <= 0:
                    raise InvalidOperation
                Pocket.objects.create(user=request.user, name=request.POST.get("name", ""), target_amount=target_amount)
                messages.success(request, "Savings pocket created.")
            except InvalidOperation:
                messages.error(request, "Enter a valid pocket target.")
        elif action == "create_transfer":
            messages.success(request, "Transfer request accepted for review.")
        return redirect("banking")
    return render(request, "dashboard/banking.html", {"beneficiaries": Beneficiary.objects.filter(user=request.user), "pockets": Pocket.objects.filter(user=request.user)})


@require_GET
@login_required
def atm(request):
    return redirect("atm_center", terminal_id="042")


@require_http_methods(["GET", "POST"])
@login_required
def atm_center(request, terminal_id):
    terminal = ATMTerminal.objects.get_or_create(terminal_id=terminal_id, defaults={"location": "Khotso Centre", "cash_units": "R50, R100, R200"})[0]
    flow_key = f"atm_flow_{terminal_id}"
    flow = request.session.get(flow_key, {"step": "service"})
    if request.method == "POST":
        return _handle_atm_command(request, terminal, terminal_id, flow_key, flow)

    flow = _select_atm_screen(request, flow_key, flow)
    left_controls, right_controls = _atm_controls(flow, request.user)
    return render(request, "dashboard/atm.html", {
        "terminal": terminal,
        "cash_transfers": CashTransfer.objects.filter(user=request.user, terminal=terminal)[:8],
        "flow": flow,
        "left_controls": left_controls,
        "right_controls": right_controls,
        "recent_activity": Transaction.objects.filter(user=request.user)[:4],
        "available_total": sum((account.balance for account in request.user.bank_accounts.filter(status=BankAccount.ACTIVE)), Decimal("0.00")),
    })


def _handle_atm_command(request, terminal, terminal_id, flow_key, flow):
    handlers = {
        "service": _atm_select_service,
        "home": _atm_home,
        "help": _atm_help,
        "account": _atm_choose_account,
        "amount": _atm_choose_amount,
        "recipient": _atm_choose_recipient,
        "edit": _atm_edit_step,
        "cancel": _atm_cancel,
        "approve": _atm_approve,
    }
    handler = handlers.get(request.POST.get("command"), _atm_continue)
    return handler(request, terminal, terminal_id, flow_key, flow)


def _atm_select_service(request, terminal, terminal_id, flow_key, flow):
    service = request.POST.get("value")
    money_services = {"withdrawal", "deposit", "cash_send", "cash_receive"}
    info_services = {"balance", "statement", "card", "recent"}
    if service in money_services:
        flow = {"service": service, "step": "account"}
    elif service in info_services:
        flow = {"service": service, "step": "info"}
    request.session[flow_key] = flow
    return _atm_redirect(terminal_id)


def _atm_home(request, terminal, terminal_id, flow_key, flow):
    request.session.pop(flow_key, None)
    return _atm_redirect(terminal_id)


def _atm_help(request, terminal, terminal_id, flow_key, flow):
    flow.update({"service": "help", "step": "info"})
    return _atm_save_flow(request, terminal_id, flow_key, flow)


def _atm_choose_account(request, terminal, terminal_id, flow_key, flow):
    selected_account = request.POST.get("value")
    if selected_account not in _atm_account_choices(request.user):
        messages.error(request, "Select one of the accounts shown on the terminal.")
        return _atm_redirect(terminal_id)
    flow.update({"account": selected_account, "step": "amount"})
    return _atm_save_flow(request, terminal_id, flow_key, flow)


def _atm_choose_amount(request, terminal, terminal_id, flow_key, flow):
    try:
        amount = Decimal(request.POST.get("value", request.POST.get("amount", "0")))
        if amount <= 0:
            raise InvalidOperation
    except InvalidOperation:
        messages.error(request, "Enter a valid amount greater than zero.")
        return _atm_save_flow(request, terminal_id, flow_key, flow)
    next_step = "recipient" if flow.get("service") in {"cash_send", "cash_receive"} else "review"
    flow.update({"amount": str(amount.quantize(Decimal("0.01"))), "step": next_step})
    return _atm_save_flow(request, terminal_id, flow_key, flow)


def _atm_choose_recipient(request, terminal, terminal_id, flow_key, flow):
    recipient = request.POST.get("recipient", "").strip()
    if not recipient:
        messages.error(request, "Enter the cellphone, alias, or voucher reference.")
        return _atm_save_flow(request, terminal_id, flow_key, flow)
    flow.update({"recipient": recipient, "step": "review"})
    return _atm_save_flow(request, terminal_id, flow_key, flow)


def _atm_edit_step(request, terminal, terminal_id, flow_key, flow):
    allowed_steps = {"account", "amount", "recipient"}
    step = request.POST.get("value", "amount")
    if step in allowed_steps:
        flow["step"] = step
    return _atm_save_flow(request, terminal_id, flow_key, flow)


def _atm_cancel(request, terminal, terminal_id, flow_key, flow):
    request.session.pop(flow_key, None)
    messages.info(request, "ATM session cancelled. No account movement was made.")
    return _atm_redirect(terminal_id)


def _atm_approve(request, terminal, terminal_id, flow_key, flow):
    account = _get_atm_account(request.user, flow.get("account", ""))
    if not flow.get("service") or account is None or not flow.get("amount"):
        messages.error(request, "Complete the service, account, and amount steps first.")
        request.session.pop(flow_key, None)
        return _atm_redirect(terminal_id)
    direction_map = {"withdrawal": CashTransfer.WITHDRAWAL, "deposit": CashTransfer.DEPOSIT, "cash_send": CashTransfer.SEND, "cash_receive": CashTransfer.RECEIVE}
    direction = direction_map.get(flow["service"])
    if direction is None:
        messages.error(request, "Select a valid ATM money service.")
        return _atm_home(request, terminal, terminal_id, flow_key, flow)
    reference = f"ATM-{terminal_id}-{secrets.token_hex(4).upper()}"
    amount = Decimal(flow["amount"])
    if direction in {CashTransfer.WITHDRAWAL, CashTransfer.SEND} and account.balance < amount:
        messages.error(request, "Insufficient available funds in the selected account.")
        return _atm_redirect(terminal_id)
    with db_transaction.atomic():
        account.balance += amount if direction in {CashTransfer.DEPOSIT, CashTransfer.RECEIVE} else -amount
        account.save(update_fields=["balance"])
        transfer = CashTransfer.objects.create(user=request.user, terminal=terminal, account=account, account_label=account.name, direction=direction, amount=amount, recipient=flow.get("recipient", ""), reference=reference)
        ATMReceipt.objects.create(transfer=transfer, receipt_number=f"KHOEBO-{reference}")
        _record_atm_transaction(request.user, transfer, direction)
    request.session.pop(flow_key, None)
    return redirect("atm_receipt", pk=transfer.pk)


def _record_atm_transaction(user, transfer, direction):
    credit_directions = {CashTransfer.DEPOSIT, CashTransfer.RECEIVE}
    transaction_direction = Transaction.CREDIT if direction in credit_directions else Transaction.DEBIT
    Transaction.objects.create(user=user, account=transfer.account, description=f"ATM {direction.replace('_', ' ')}", category="ATM", amount=transfer.amount, direction=transaction_direction, status="Completed")


def _atm_continue(request, terminal, terminal_id, flow_key, flow):
    return _atm_save_flow(request, terminal_id, flow_key, flow)


def _atm_save_flow(request, terminal_id, flow_key, flow):
    request.session[flow_key] = flow
    request.session.modified = True
    return _atm_redirect(terminal_id)


def _atm_redirect(terminal_id):
    return redirect("atm_center", terminal_id=terminal_id)


def _select_atm_screen(request, flow_key, flow):
    requested_service = request.GET.get("service")
    money_services = {"withdrawal", "deposit", "cash_send", "cash_receive"}
    info_services = {"balance", "statement", "card", "recent"}
    if requested_service in money_services:
        flow = {"service": requested_service, "step": "account"}
    elif requested_service in info_services:
        flow = {"service": requested_service, "step": "info"}
    else:
        return flow
    request.session[flow_key] = flow
    return flow


def _atm_controls(flow, user):
    builders = {
        "service": _atm_service_controls,
        "account": _atm_account_controls,
        "amount": _atm_amount_controls,
        "recipient": _atm_recipient_controls,
        "review": _atm_review_controls,
    }
    left, right = builders.get(flow.get("step"), _atm_info_controls)(flow, user)
    return _fill_atm_controls(left), _fill_atm_controls(right)


def _atm_service_controls(flow, user):
    services = [("Withdraw cash", "withdrawal"), ("Deposit cash", "deposit"), ("Send cash", "cash_send"), ("Receive cash", "cash_receive")]
    info = [("Balance", "balance"), ("Mini statement", "statement"), ("Card services", "card"), ("Recent activity", "recent")]
    return ([_atm_key(label, "service", value) for label, value in services], [_atm_key(label, "service", value) for label, value in info])


def _atm_account_controls(flow, user):
    left = [_atm_key(account, "account", account) for account in _atm_account_choices(user)]
    return left, [_atm_key(ATM_BACK_LABEL, "home")]


def _atm_amount_controls(flow, user):
    left = [_atm_key(f"R {amount}", "amount", amount) for amount in ["100", "200", "500", "1000"]]
    return left, [_atm_key("Change account", "edit", "account")]


def _atm_recipient_controls(flow, user):
    names = list(user.beneficiaries.values_list("name", flat=True)[:3])
    left = [_atm_key(name, "recipient", name) for name in names]
    left.append(_atm_key("Enter recipient", "edit", "recipient"))
    return left, [_atm_key("Change amount", "edit", "amount")]


def _atm_review_controls(flow, user):
    left = [_atm_key("Change account", "edit", "account"), _atm_key("Change amount", "edit", "amount")]
    if flow.get("service") in {"cash_send", "cash_receive"}:
        left.append(_atm_key("Change recipient", "edit", "recipient"))
    return left, [_atm_key("Approve transaction", "approve")]


def _atm_info_controls(flow, user):
    return [_atm_key(ATM_BACK_LABEL, "home")], [_atm_key("New session", "home")]


def _atm_key(label, command, value=""):
    return {"label": label, "command": command, "value": value}


def _fill_atm_controls(controls):
    fillers = [
        _atm_key("Need help", "help"),
        _atm_key("Cancel session", "cancel"),
        _atm_key(ATM_BACK_LABEL, "home"),
        _atm_key("Start over", "home"),
    ]
    labels = {control["label"] for control in controls}
    for filler in fillers:
        if len(controls) == 4:
            break
        if filler["label"] not in labels:
            controls.append(filler)
            labels.add(filler["label"])
    return controls[:4]


def _atm_account_choices(user):
    return [f"{account.name} · {account.masked_number}" for account in user.bank_accounts.filter(status=BankAccount.ACTIVE)]


def _get_atm_account(user, account_label):
    for account in user.bank_accounts.filter(status=BankAccount.ACTIVE):
        if f"{account.name} · {account.masked_number}" == account_label:
            return account
    return None


@require_GET
@login_required
def atm_receipt(request, pk):
    transfer = get_object_or_404(CashTransfer.objects.select_related("terminal", "receipt"), pk=pk, user=request.user)
    return render(request, "dashboard/atm_receipt.html", {"transfer": transfer, "receipt": transfer.receipt})


@require_http_methods(["GET", "POST"])
@login_required
def trading(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_watchlist":
            instrument = Instrument.objects.get(pk=request.POST["instrument_id"])
            WatchlistItem.objects.get_or_create(user=request.user, instrument=instrument)
            messages.success(request, f"{instrument.symbol} added to your watchlist.")
        elif action == "create_order":
            instrument = Instrument.objects.get(pk=request.POST["instrument_id"])
            TradeOrder.objects.create(user=request.user, instrument=instrument, side=request.POST["side"], quantity=max(1, int(request.POST["quantity"])), limit_price=Decimal(request.POST["limit_price"]))
            messages.success(request, f"{instrument.symbol} order queued.")
        return redirect("trading")
    return render(request, "dashboard/trading.html", {"instruments": Instrument.objects.all(), "watchlist": WatchlistItem.objects.filter(user=request.user).select_related("instrument"), "orders": TradeOrder.objects.filter(user=request.user).select_related("instrument")})


@require_POST
@login_required
def action_result(request):
    action = request.POST.get("action", "Action")
    return render(request, "dashboard/action_result.html", {"message": f"{action} request accepted for review."})


@require_GET
@login_required
def transactions(request):
    queryset = Transaction.objects.filter(user=request.user).select_related("account")
    account_id = request.GET.get("account")
    if account_id:
        queryset = queryset.filter(account_id=account_id)
    direction = request.GET.get("direction")
    if direction in {Transaction.CREDIT, Transaction.DEBIT}:
        queryset = queryset.filter(direction=direction)
    search = request.GET.get("q", "").strip()
    if search:
        queryset = queryset.filter(Q(description__icontains=search) | Q(category__icontains=search) | Q(account__name__icontains=search))
    months = request.GET.get("months", "")
    if months in {"1", "3", "6", "9", "12"}:
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30 * int(months)))
    page = Paginator(queryset, 15).get_page(request.GET.get("page"))
    return render(request, "dashboard/transactions.html", {"page_obj": page, "transactions": page.object_list, "accounts": BankAccount.objects.filter(user=request.user), "selected_account": account_id, "selected_direction": direction, "selected_months": months, "search_query": search})


@require_GET
@login_required
def statement_csv(request, pk):
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    rows = Transaction.objects.filter(user=request.user, account=account).order_by("created_at")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="khoebo-statement-{account.account_number[-4:]}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Date", "Description", "Category", "Direction", "Amount (ZAR)", "Status"])
    for row in rows:
        writer.writerow([row.created_at.isoformat(), row.description, row.category, row.direction, row.amount, row.status])
    return response


@require_GET
@login_required
def mobile(request):
    return render(request, "dashboard/mobile.html")


@login_required
def payments(request):
    if request.method == "POST":
        action = request.POST.get("action", "create")
        if action == "execute":
            return _execute_payment(request, request.POST.get("payment_id"))
        account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user, status=BankAccount.ACTIVE)
        try:
            amount = _positive_amount(request.POST.get("amount", "0"))
        except InvalidOperation:
            messages.error(request, "Enter a valid payment amount.")
            return redirect("payments")
        kind = request.POST.get("kind", Payment.PAYMENT)
        beneficiary = request.POST.get("beneficiary", "").strip()
        reference = request.POST.get("reference", "").strip()
        if kind not in {Payment.PAYMENT, Payment.TRANSFER} or not beneficiary or not reference:
            messages.error(request, "Choose a payment type and enter a recipient and reference.")
            return redirect("payments")
        payment = Payment.objects.create(user=request.user, account=account, kind=kind, beneficiary=beneficiary, amount=amount, reference=reference, status="Draft")
        messages.success(request, f"{payment.get_kind_display()} draft saved. Review it before sending.")
        return redirect("payments")
    accounts_for_user = BankAccount.objects.filter(user=request.user, status=BankAccount.ACTIVE)
    context = {"payments": Payment.objects.filter(user=request.user).select_related("account").prefetch_related("proof")[:20], "accounts": accounts_for_user, "available_total": sum((account.balance for account in accounts_for_user), Decimal("0.00"))}
    return render(request, "dashboard/payments.html", context)


def _positive_amount(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as error:
        raise InvalidOperation from error
    if amount <= 0:
        raise InvalidOperation
    return amount.quantize(Decimal("0.01"))


def _execute_payment(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, user=request.user, status="Draft")
    account = get_object_or_404(BankAccount, pk=payment.account_id, user=request.user, status=BankAccount.ACTIVE)
    if account.balance < payment.amount:
        messages.error(request, "Insufficient funds in the selected account.")
        return redirect("payments")
    with db_transaction.atomic():
        account.balance -= payment.amount
        account.save(update_fields=["balance"])
        payment.status = "Completed"
        payment.save(update_fields=["status"])
        Transaction.objects.create(user=request.user, account=account, description=f"{payment.get_kind_display()} to {payment.beneficiary}", category=payment.get_kind_display(), amount=payment.amount, direction=Transaction.DEBIT, status="Completed")
        proof = ProofOfPayment.objects.create(user=request.user, payment=payment, receipt_number=f"KHOEBO-{payment.pk:08d}")
    messages.success(request, f"Payment complete. Proof {proof.receipt_number} is ready.")
    return redirect("payments")


@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk, user=request.user, status="Draft")
    if request.method == "POST":
        try:
            amount = _positive_amount(request.POST.get("amount", "0"))
        except InvalidOperation:
            messages.error(request, "Enter a valid payment amount.")
        else:
            account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user, status=BankAccount.ACTIVE)
            kind = request.POST.get("kind", payment.kind)
            beneficiary = request.POST.get("beneficiary", "").strip()
            reference = request.POST.get("reference", "").strip()
            if kind not in {Payment.PAYMENT, Payment.TRANSFER} or not beneficiary or not reference:
                messages.error(request, "Choose a valid type and enter a recipient and reference.")
            else:
                payment.kind = kind
                payment.account = account
                payment.beneficiary = beneficiary
                payment.amount = amount
                payment.reference = reference
                payment.save(update_fields=["account", "kind", "beneficiary", "amount", "reference"])
                messages.success(request, "Draft updated.")
                return redirect("payments")
    return render(request, "dashboard/payment_edit.html", {"payment": payment})


@require_POST
@login_required
def payment_delete(request, pk):
    Payment.objects.filter(pk=pk, user=request.user, status="Draft").delete()
    messages.success(request, "Draft deleted. Completed payments remain in your transaction history.")
    return redirect("payments")


@login_required
def accounts(request):
    if request.method == "POST":
        account_type = request.POST.get("account_type", BankAccount.TRANSACTION)
        if account_type not in {BankAccount.TRANSACTION, BankAccount.SAVINGS}:
            messages.error(request, "Choose a valid account type.")
            return redirect("accounts")
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "Enter an account name.")
            return redirect("accounts")
        number = f"{secrets.randbelow(90000000) + 10000000}"
        account = BankAccount.objects.create(user=request.user, name=name, account_number=number, account_type=account_type)
        messages.success(request, f"{account.get_account_type_display()} account created.")
        return redirect("accounts")
    return render(request, "dashboard/accounts.html", {"accounts": BankAccount.objects.filter(user=request.user)})


@require_GET
@login_required
def account_info(request, pk):
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    transactions = Transaction.objects.filter(user=request.user, account=account)
    return render(request, "dashboard/account_info.html", {"account": account, "transactions": transactions})


@login_required
def account_edit(request, pk):
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    if request.method == "POST":
        account.name = request.POST.get("name", "").strip()
        status = request.POST.get("status", account.status)
        if not account.name or status not in {BankAccount.ACTIVE, BankAccount.FROZEN}:
            messages.error(request, "Enter a name and valid account status.")
        else:
            account.status = status
            account.save(update_fields=["name", "status"])
            messages.success(request, "Account updated.")
            return redirect("accounts")
    return render(request, "dashboard/account_edit.html", {"account": account})


@require_POST
@login_required
def account_delete(request, pk):
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    has_history = Transaction.objects.filter(account=account).exists() or Payment.objects.filter(account=account).exists() or CashTransfer.objects.filter(account=account).exists()
    if account.balance != 0 or has_history or account.service_purchases.exists():
        messages.error(request, "An account with a balance or transaction history cannot be deleted. Freeze it instead.")
    else:
        account.delete()
        messages.success(request, "Empty account deleted.")
    return redirect("accounts")


@login_required
def cards(request):
    accounts_for_user = BankAccount.objects.filter(user=request.user)
    if request.method == "POST":
        action = request.POST.get("action")
        card = get_object_or_404(BankCard, pk=request.POST.get("card_id"), user=request.user) if request.POST.get("card_id") else None
        if action == "create":
            account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user)
            last_four = request.POST.get("last_four", "")
            if len(last_four) != 4 or not last_four.isdigit():
                messages.error(request, "Enter only the final four card digits.")
            else:
                BankCard.objects.create(user=request.user, account=account, label=request.POST.get("label", "KHOEBO card"), card_type=request.POST.get("card_type", BankCard.PHYSICAL), last_four=last_four)
                messages.success(request, "Card added using masked details only.")
        elif action == "toggle" and card:
            card.status = BankCard.FROZEN if card.status == BankCard.ACTIVE else BankCard.ACTIVE
            card.save(update_fields=["status"])
            messages.success(request, f"Card is now {card.status}.")
        return redirect("cards")
    return render(request, "dashboard/cards.html", {"cards": BankCard.objects.filter(user=request.user).select_related("account"), "accounts": accounts_for_user})


@require_POST
@login_required
def card_delete(request, pk):
    BankCard.objects.filter(pk=pk, user=request.user).delete()
    messages.success(request, "Card record removed.")
    return redirect("cards")


@login_required
def card_edit(request, pk):
    card = get_object_or_404(BankCard, pk=pk, user=request.user)
    accounts_for_user = BankAccount.objects.filter(user=request.user)
    if request.method == "POST":
        card.account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user)
        card.label = request.POST.get("label", "").strip()
        card.status = request.POST.get("status", card.status)
        if card.status not in dict(BankCard.CARD_STATUSES) or not card.label:
            messages.error(request, "Enter a label and valid card status.")
        else:
            card.save(update_fields=["account", "label", "status"])
            messages.success(request, "Card updated.")
            return redirect("cards")
    return render(request, "dashboard/card_edit.html", {"card": card, "accounts": accounts_for_user})


@login_required
def debit_orders(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user)
            try:
                amount = _positive_amount(request.POST.get("amount", "0"))
            except InvalidOperation:
                messages.error(request, "Enter a valid debit order amount.")
                return redirect("debit_orders")
            DebitOrder.objects.create(user=request.user, account=account, payee=request.POST.get("payee", "").strip(), amount=amount, mandate_reference=request.POST.get("mandate_reference", "").strip(), next_date=request.POST.get("next_date"))
            messages.success(request, "Debit order mandate saved.")
        elif action == "toggle":
            mandate = get_object_or_404(DebitOrder, pk=request.POST.get("mandate_id"), user=request.user)
            mandate.status = DebitOrder.PAUSED if mandate.status == DebitOrder.ACTIVE else DebitOrder.ACTIVE
            mandate.save(update_fields=["status"])
            messages.success(request, f"Debit order {mandate.status}.")
        return redirect("debit_orders")
    return render(request, "dashboard/debit_orders.html", {"orders": DebitOrder.objects.filter(user=request.user).select_related("account"), "accounts": BankAccount.objects.filter(user=request.user, status=BankAccount.ACTIVE)})


@require_POST
@login_required
def debit_order_delete(request, pk):
    DebitOrder.objects.filter(pk=pk, user=request.user).delete()
    messages.success(request, "Debit order mandate deleted.")
    return redirect("debit_orders")


@login_required
def debit_order_edit(request, pk):
    mandate = get_object_or_404(DebitOrder, pk=pk, user=request.user)
    if request.method == "POST":
        try:
            amount = _positive_amount(request.POST.get("amount", "0"))
        except InvalidOperation:
            messages.error(request, "Enter a valid mandate amount.")
        else:
            mandate.account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user)
            mandate.payee = request.POST.get("payee", "").strip()
            mandate.amount = amount
            mandate.mandate_reference = request.POST.get("mandate_reference", "").strip()
            mandate.next_date = request.POST.get("next_date")
            if mandate.payee and mandate.mandate_reference:
                mandate.save(update_fields=["account", "payee", "amount", "mandate_reference", "next_date"])
                messages.success(request, "Debit order updated.")
                return redirect("debit_orders")
            messages.error(request, "Payee and mandate reference are required.")
    return render(request, "dashboard/debit_order_edit.html", {"mandate": mandate, "accounts": BankAccount.objects.filter(user=request.user)})


@login_required
def services(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user, status=BankAccount.ACTIVE)
            try:
                amount = _positive_amount(request.POST.get("amount", "0"))
            except InvalidOperation:
                messages.error(request, "Enter a valid service amount.")
                return redirect("services")
            service_type = request.POST.get("service_type")
            if service_type not in dict(ServicePurchase.SERVICE_TYPES):
                messages.error(request, "Choose a supported service.")
                return redirect("services")
            purchase = ServicePurchase.objects.create(user=request.user, account=account, service_type=service_type, recipient=request.POST.get("recipient", "").strip(), amount=amount, reference=request.POST.get("reference", ""))
            messages.success(request, f"{purchase.get_service_type_display()} purchase saved as a draft.")
        elif action == "execute":
            purchase = get_object_or_404(ServicePurchase, pk=request.POST.get("purchase_id"), user=request.user, status=ServicePurchase.DRAFT)
            if purchase.account.balance < purchase.amount:
                messages.error(request, "Insufficient funds in the selected account.")
                return redirect("services")
            with db_transaction.atomic():
                purchase.account.balance -= purchase.amount
                purchase.account.save(update_fields=["balance"])
                transaction_entry = Transaction.objects.create(user=request.user, account=purchase.account, description=f"{purchase.get_service_type_display()} for {purchase.recipient}", category="Value-added services", amount=purchase.amount, direction=Transaction.DEBIT, status="Completed")
                purchase.transaction = transaction_entry
                purchase.status = ServicePurchase.COMPLETED
                purchase.save(update_fields=["transaction", "status"])
            messages.success(request, f"{purchase.get_service_type_display()} complete. Reference {transaction_entry.pk}.")
        return redirect("services")
    return render(request, "dashboard/services.html", {"purchases": ServicePurchase.objects.filter(user=request.user).select_related("account"), "accounts": BankAccount.objects.filter(user=request.user, status=BankAccount.ACTIVE)})


@login_required
def service_purchase_edit(request, pk):
    purchase = get_object_or_404(ServicePurchase, pk=pk, user=request.user, status=ServicePurchase.DRAFT)
    if request.method == "POST":
        try:
            amount = _positive_amount(request.POST.get("amount", "0"))
        except InvalidOperation:
            messages.error(request, "Enter a valid service amount.")
        else:
            account = get_object_or_404(BankAccount, pk=request.POST.get("account_id"), user=request.user, status=BankAccount.ACTIVE)
            service_type = request.POST.get("service_type", purchase.service_type)
            if service_type not in dict(ServicePurchase.SERVICE_TYPES):
                messages.error(request, "Choose a supported service.")
                return render(request, "dashboard/service_edit.html", {"purchase": purchase, "accounts": BankAccount.objects.filter(user=request.user, status=BankAccount.ACTIVE)})
            purchase.account = account
            purchase.service_type = service_type
            purchase.recipient = request.POST.get("recipient", "").strip()
            purchase.amount = amount
            purchase.reference = request.POST.get("reference", "")
            purchase.save(update_fields=["account", "service_type", "recipient", "amount", "reference"])
            messages.success(request, "Service draft updated.")
            return redirect("services")
    return render(request, "dashboard/service_edit.html", {"purchase": purchase, "accounts": BankAccount.objects.filter(user=request.user, status=BankAccount.ACTIVE)})


@require_POST
@login_required
def service_purchase_delete(request, pk):
    ServicePurchase.objects.filter(pk=pk, user=request.user, status=ServicePurchase.DRAFT).delete()
    messages.success(request, "Service draft deleted.")
    return redirect("services")


@require_GET
@login_required
def payment_proof(request, pk):
    payment = get_object_or_404(Payment, pk=pk, user=request.user, status="Completed")
    proof, _ = ProofOfPayment.objects.get_or_create(user=request.user, payment=payment, defaults={"receipt_number": f"KHOEBO-{payment.pk:08d}"})
    return render(request, "dashboard/proof.html", {"payment": payment, "proof": proof})


def _seed_demo_data(user):
    everyday, _ = BankAccount.objects.get_or_create(user=user, account_type=BankAccount.TRANSACTION, defaults={"name": "Everyday account", "account_number": f"1048{user.pk:06d}", "balance": Decimal("24680.00")})
    BankAccount.objects.get_or_create(user=user, account_type=BankAccount.SAVINGS, defaults={"name": "Rainy day savings", "account_number": f"2048{user.pk:06d}", "balance": Decimal("5050.00")})
    instruments = [
        ("KHOE", "Khoebo Holdings", Decimal("128.40"), Decimal("2.80")),
        ("NOVA", "Nova Energy", Decimal("76.15"), Decimal("0.90")),
        ("MARA", "Mara Infrastructure", Decimal("44.20"), Decimal("-1.20")),
    ]
    for symbol, name, price, day_change in instruments:
        instrument, _ = Instrument.objects.get_or_create(symbol=symbol, defaults={"name": name, "price": price, "day_change": day_change})
        if not WatchlistItem.objects.filter(user=user, instrument=instrument).exists() and symbol in {"KHOE", "NOVA"}:
            WatchlistItem.objects.create(user=user, instrument=instrument)
    if not Pocket.objects.filter(user=user).exists():
        Pocket.objects.bulk_create([
            Pocket(user=user, name="Rainy day", target_amount=Decimal("10000.00"), balance=Decimal("3200.00")),
            Pocket(user=user, name="Travel", target_amount=Decimal("8000.00"), balance=Decimal("1850.00")),
        ])
    if not Beneficiary.objects.filter(user=user).exists():
        Beneficiary.objects.bulk_create([
            Beneficiary(user=user, name="KHOEBO Savings", account_identifier="•••• 2048", bank_label="KHOEBO account"),
            Beneficiary(user=user, name="Home services", account_identifier="KHOEBO-HOME-01", bank_label="Saved recipient"),
        ])
    if not BankCard.objects.filter(user=user).exists():
        BankCard.objects.create(user=user, account=everyday, label="Everyday debit", card_type=BankCard.PHYSICAL, last_four="2048")
    if not DebitOrder.objects.filter(user=user).exists():
        DebitOrder.objects.create(user=user, account=everyday, payee="Home services", amount=Decimal("1250.00"), mandate_reference="KHOEBO-MANDATE-01", next_date=date.today() + timedelta(days=8))
    if not ServicePurchase.objects.filter(user=user).exists():
        ServicePurchase.objects.create(user=user, account=everyday, service_type=ServicePurchase.AIRTIME, recipient="0820000000", amount=Decimal("50.00"), reference="Demo airtime top-up")
    CustomerProfile.objects.get_or_create(user=user, defaults={"phone": "+27 82 000 0000", "verified": True, "two_factor_enabled": True})
    if not Bill.objects.filter(user=user).exists():
        Bill.objects.bulk_create([
            Bill(user=user, payee="KHOEBO Mobile", amount=Decimal("599.00"), due_date=date.today() + timedelta(days=5)),
            Bill(user=user, payee="Home services", amount=Decimal("1250.00"), due_date=date.today() + timedelta(days=12)),
        ])
    if not Invoice.objects.filter(user=user).exists():
        Invoice.objects.create(user=user, invoice_number="INV-0001", name="Monthly services", bill_to="Demo recipient", amount=Decimal("2400.00"), issue_date=date.today(), due_date=date.today() + timedelta(days=30))
    if not PaymentMethod.objects.filter(user=user).exists():
        PaymentMethod.objects.create(user=user, label="Everyday card", kind="Card", masked_identifier="•••• 2048", is_default=True)
    if not Notification.objects.filter(user=user).exists():
        Notification.objects.bulk_create([
            Notification(user=user, title="Account ready", body="Your KHOEBO account workspace is ready.", kind="success"),
            Notification(user=user, title="Security review", body="Review your trusted devices and transaction limits.", kind="info"),
        ])
    if not RewardEntry.objects.filter(user=user).exists():
        RewardEntry.objects.create(user=user, action=RewardEntry.EARN, points=1240, description="Welcome rewards balance")


@require_POST
@login_required
def beneficiary_delete(request, pk):
    Beneficiary.objects.filter(pk=pk, user=request.user).delete()
    return redirect("banking")


@login_required
def beneficiary_edit(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk, user=request.user)
    if request.method == "POST":
        beneficiary.name = request.POST.get("name", "").strip()
        beneficiary.account_identifier = request.POST.get("account_identifier", "").strip()
        beneficiary.bank_label = request.POST.get("bank_label", "KHOEBO account").strip()
        if beneficiary.name and beneficiary.account_identifier:
            beneficiary.save(update_fields=["name", "account_identifier", "bank_label"])
            messages.success(request, "Beneficiary updated.")
            return redirect("banking")
        messages.error(request, "Name and account or alias are required.")
    fields = [
        {"name": "name", "label": "Name", "value": beneficiary.name, "type": "text"},
        {"name": "account_identifier", "label": "Account or alias", "value": beneficiary.account_identifier, "type": "text"},
        {"name": "bank_label", "label": "Bank label", "value": beneficiary.bank_label, "type": "text"},
    ]
    return render(request, "dashboard/record_edit.html", {"record_type": "Beneficiary", "fields": fields})


@require_POST
@login_required
def pocket_delete(request, pk):
    Pocket.objects.filter(pk=pk, user=request.user).delete()
    return redirect("banking")


@login_required
def pocket_edit(request, pk):
    pocket = get_object_or_404(Pocket, pk=pk, user=request.user)
    if request.method == "POST":
        try:
            target = Decimal(request.POST.get("target_amount", "0"))
            rate = Decimal(request.POST.get("rate", "0"))
            if target <= 0 or rate < 0:
                raise InvalidOperation
        except InvalidOperation:
            messages.error(request, "Enter a positive target and a non-negative rate.")
        else:
            pocket.name = request.POST.get("name", "").strip()
            pocket.target_amount = target
            pocket.rate = rate
            pocket.save(update_fields=["name", "target_amount", "rate"])
            messages.success(request, "Savings pocket updated.")
            return redirect("banking")
    fields = [
        {"name": "name", "label": "Pocket name", "value": pocket.name, "type": "text"},
        {"name": "target_amount", "label": "Target amount", "value": pocket.target_amount, "type": "number"},
        {"name": "rate", "label": "Projected rate", "value": pocket.rate, "type": "number"},
    ]
    return render(request, "dashboard/record_edit.html", {"record_type": "Savings pocket", "fields": fields})


@login_required
def rewards(request):
    if request.method == "POST":
        action = request.POST.get("action")
        try:
            points = int(request.POST.get("points", "0"))
            if points <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Enter a points amount greater than zero.")
            return redirect("rewards")
        if action == "redeem" and points > _reward_balance(request.user):
            messages.error(request, "You do not have enough points for that redemption.")
        elif action in {RewardEntry.EARN, RewardEntry.REDEEM, RewardEntry.ADJUST}:
            RewardEntry.objects.create(user=request.user, action=action, points=points, description=request.POST.get("description", "KHOEBO rewards activity"))
            messages.success(request, "Reward activity recorded.")
        return redirect("rewards")
    entries = RewardEntry.objects.filter(user=request.user)
    return render(request, "dashboard/rewards.html", {"entries": entries, "points_balance": _reward_balance(request.user)})


@login_required
def reward_edit(request, pk):
    entry = get_object_or_404(RewardEntry, pk=pk, user=request.user)
    if request.method == "POST":
        points = _positive_points(request.POST.get("points", "0"))
        if points is None:
            messages.error(request, "Enter a points amount greater than zero.")
        else:
            action = request.POST.get("action", entry.action)
            error = _reward_edit_error(request.user, entry, action, points)
            if error:
                messages.error(request, error)
            else:
                entry.action = action
                entry.points = points
                entry.description = request.POST.get("description", "").strip()
                entry.save(update_fields=["action", "points", "description"])
                messages.success(request, "Reward entry updated.")
                return redirect("rewards")
    return render(request, REWARD_EDIT_TEMPLATE, {"entry": entry})


def _positive_points(value):
    try:
        points = int(value)
    except (TypeError, ValueError):
        return None
    return points if points > 0 else None


def _reward_edit_error(user, entry, action, points):
    if action not in REWARD_ACTIONS:
        return "Select a valid rewards action."
    prior_effect = -entry.points if entry.action == RewardEntry.REDEEM else entry.points
    updated_effect = -points if action == RewardEntry.REDEEM else points
    if _reward_balance(user) - prior_effect + updated_effect < 0:
        return "That update would make your rewards balance negative."
    return None


@require_POST
@login_required
def reward_delete(request, pk):
    RewardEntry.objects.filter(pk=pk, user=request.user).delete()
    messages.success(request, "Reward entry deleted.")
    return redirect("rewards")


def _reward_balance(user):
    balance = 0
    for entry in RewardEntry.objects.filter(user=user).only("action", "points"):
        balance += -entry.points if entry.action == RewardEntry.REDEEM else entry.points
    return max(balance, 0)


@require_POST
@login_required
def watchlist_delete(request, pk):
    WatchlistItem.objects.filter(pk=pk, user=request.user).delete()
    return redirect("trading")


@login_required
def order_edit(request, pk):
    order = TradeOrder.objects.select_related("instrument").get(pk=pk, user=request.user)
    if request.method == "POST":
        order.side = request.POST["side"]
        order.quantity = max(1, int(request.POST["quantity"]))
        order.limit_price = Decimal(request.POST["limit_price"])
        order.save(update_fields=["side", "quantity", "limit_price"])
        messages.success(request, "Order updated.")
        return redirect("trading")
    return render(request, "dashboard/order_edit.html", {"order": order})


@require_POST
@login_required
def order_delete(request, pk):
    TradeOrder.objects.filter(pk=pk, user=request.user).update(status="Cancelled")
    messages.success(request, "Order cancelled.")
    return redirect("trading")


@login_required
def bill(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_bill":
            Bill.objects.create(user=request.user, payee=request.POST.get("payee", ""), amount=Decimal(request.POST.get("amount", "0")), due_date=request.POST.get("due_date"))
            messages.success(request, "Bill added.")
        elif action == "pay_bill":
            Bill.objects.filter(pk=request.POST.get("bill_id"), user=request.user).update(status="Paid")
            messages.success(request, "Bill marked as paid.")
        return redirect("bill")
    return render(request, "dashboard/bills.html", {"bills": Bill.objects.filter(user=request.user)})


@require_POST
@login_required
def bill_delete(request, pk):
    Bill.objects.filter(pk=pk, user=request.user).delete()
    return redirect("bill")


@require_GET
@login_required
def invoice(request):
    return render(request, "dashboard/invoices.html", {"invoices": Invoice.objects.filter(user=request.user)})


@login_required
def create_invoice(request):
    if request.method == "POST":
        Invoice.objects.create(user=request.user, invoice_number=f"INV-{Invoice.objects.filter(user=request.user).count() + 1:04d}", name=request.POST.get("name", ""), bill_to=request.POST.get("bill_to", ""), amount=Decimal(request.POST.get("amount", "0")), issue_date=request.POST.get("issue_date"), due_date=request.POST.get("due_date"))
        messages.success(request, "Invoice created.")
        return redirect("invoice")
    return render(request, "dashboard/invoice_form.html", {"today": date.today(), "due_date": date.today() + timedelta(days=30)})


@require_POST
@login_required
def invoice_delete(request, pk):
    Invoice.objects.filter(pk=pk, user=request.user).delete()
    return redirect("invoice")


@login_required
def profile(request):
    profile_record, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", request.user.first_name)
        request.user.last_name = request.POST.get("last_name", request.user.last_name)
        request.user.email = request.POST.get("email", request.user.email)
        request.user.save(update_fields=["first_name", "last_name", "email"])
        profile_record.phone = request.POST.get("phone", profile_record.phone)
        profile_record.save(update_fields=["phone"])
        messages.success(request, "Profile updated.")
        return redirect("profile")
    return render(request, "dashboard/profile.html", {"profile_record": profile_record})


@login_required
def notification(request):
    if request.method == "POST":
        if request.POST.get("action") == "read_all":
            Notification.objects.filter(user=request.user).update(is_read=True)
        elif request.POST.get("action") == "delete":
            Notification.objects.filter(pk=request.POST.get("notification_id"), user=request.user).delete()
        return redirect("notification")
    return render(request, "dashboard/notifications.html", {"notifications": Notification.objects.filter(user=request.user)})


@login_required
def settings_payment_method(request):
    if request.method == "POST":
        if request.POST.get("action") == "add":
            PaymentMethod.objects.create(user=request.user, label=request.POST.get("label", ""), kind=request.POST.get("kind", "Card"), masked_identifier=request.POST.get("masked_identifier", ""), is_default=not PaymentMethod.objects.filter(user=request.user).exists())
        elif request.POST.get("action") == "delete":
            PaymentMethod.objects.filter(pk=request.POST.get("method_id"), user=request.user).delete()
        return redirect("settings_payment_method")
    return render(request, SETTINGS_TEMPLATE, {"section": "Payment methods", "methods": PaymentMethod.objects.filter(user=request.user)})


@login_required
def settings_api(request):
    if request.method == "POST":
        if request.POST.get("action") == "generate":
            APIKey.objects.create(user=request.user, name=request.POST.get("name", "Mobile integration"), key_prefix=f"khoebo_{secrets.token_hex(5)}")
        elif request.POST.get("action") == "revoke":
            APIKey.objects.filter(pk=request.POST.get("key_id"), user=request.user).update(status="Revoked")
        return redirect("settings_api")
    return render(request, SETTINGS_TEMPLATE, {"section": "API access", "api_keys": APIKey.objects.filter(user=request.user)})


@login_required
def settings_security(request):
    profile_record, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile_record.two_factor_enabled = request.POST.get("two_factor_enabled") == "on"
        profile_record.login_alerts = request.POST.get("login_alerts") == "on"
        profile_record.save(update_fields=["two_factor_enabled", "login_alerts"])
        messages.success(request, "Security settings updated.")
        return redirect("settings_security")
    return render(request, SETTINGS_TEMPLATE, {"section": "Security", "profile_record": profile_record})


@require_GET
@login_required
def settings_page(request, section):
    profile_record, _ = CustomerProfile.objects.get_or_create(user=request.user)
    return render(request, SETTINGS_TEMPLATE, {"section": section, "profile_record": profile_record, "transactions": Transaction.objects.filter(user=request.user)[:12]})


@login_required
def lock(request):
    profile_record, _ = CustomerProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        profile_record.locked = True
        profile_record.save(update_fields=["locked"])
        logout(request)
        return redirect("login")
    return render(request, "dashboard/lock.html", {"profile_record": profile_record})


@require_GET
@login_required
def otp(request):
    return render(request, "dashboard/otp.html")


@require_GET
def reset(request):
    return render(request, "dashboard/reset.html")
