from django.contrib.auth.models import User
from django.db import models


class Transaction(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"
    DIRECTIONS = [(CREDIT, "Credit"), (DEBIT, "Debit")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    account = models.ForeignKey("BankAccount", on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    description = models.CharField(max_length=140)
    category = models.CharField(max_length=60, default="Everyday")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    direction = models.CharField(max_length=6, choices=DIRECTIONS)
    status = models.CharField(max_length=30, default="Completed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Payment(models.Model):
    PAYMENT = "payment"
    TRANSFER = "transfer"
    KINDS = [(PAYMENT, "Payment"), (TRANSFER, "Transfer")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    account = models.ForeignKey("BankAccount", on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    kind = models.CharField(max_length=10, choices=KINDS, default=PAYMENT)
    beneficiary = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=140)
    status = models.CharField(max_length=30, default="Submitted")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Beneficiary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="beneficiaries")
    name = models.CharField(max_length=120)
    account_identifier = models.CharField(max_length=80)
    bank_label = models.CharField(max_length=80, default="KHOEBO account")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]


class Pocket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pockets")
    name = models.CharField(max_length=60)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["user", "name"], name="unique_user_pocket_name")]


class PocketMovement(models.Model):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    DIRECTIONS = [(DEPOSIT, "Deposit to pocket"), (WITHDRAW, "Withdraw from pocket")]

    pocket = models.ForeignKey(Pocket, on_delete=models.CASCADE, related_name="movements")
    account = models.ForeignKey("BankAccount", on_delete=models.SET_NULL, null=True, blank=True, related_name="pocket_movements")
    direction = models.CharField(max_length=10, choices=DIRECTIONS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Instrument(models.Model):
    symbol = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    day_change = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, default="ZAR")

    class Meta:
        ordering = ["symbol"]


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="watchers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["instrument__symbol"]
        constraints = [models.UniqueConstraint(fields=["user", "instrument"], name="unique_user_watchlist_instrument")]


class TradeOrder(models.Model):
    BUY = "buy"
    SELL = "sell"
    SIDES = [(BUY, "Buy"), (SELL, "Sell")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trade_orders")
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT, related_name="orders")
    side = models.CharField(max_length=4, choices=SIDES)
    quantity = models.PositiveIntegerField()
    limit_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, default="Queued")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ATMTerminal(models.Model):
    terminal_id = models.CharField(max_length=20, primary_key=True)
    location = models.CharField(max_length=120)
    status = models.CharField(max_length=30, default="Online")
    cash_units = models.CharField(max_length=120, default="R50, R100, R200")
    contactless = models.BooleanField(default=True)
    cardless = models.BooleanField(default=True)

    class Meta:
        ordering = ["terminal_id"]


class CashTransfer(models.Model):
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    SEND = "send"
    RECEIVE = "receive"
    DIRECTIONS = [(WITHDRAWAL, "Withdrawal"), (DEPOSIT, "Deposit"), (SEND, "Cash send"), (RECEIVE, "Cash receive")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cash_transfers")
    terminal = models.ForeignKey(ATMTerminal, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey("BankAccount", on_delete=models.SET_NULL, null=True, blank=True, related_name="cash_transfers")
    account_label = models.CharField(max_length=80, default="Everyday account")
    direction = models.CharField(max_length=10, choices=DIRECTIONS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recipient = models.CharField(max_length=120, blank=True)
    reference = models.CharField(max_length=80)
    status = models.CharField(max_length=30, default="Completed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ATMReceipt(models.Model):
    transfer = models.OneToOneField(CashTransfer, on_delete=models.CASCADE, related_name="receipt")
    receipt_number = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ProofOfPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="proofs_of_payment")
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="proof")
    receipt_number = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bills")
    service_provider = models.ForeignKey("Beneficiary", on_delete=models.SET_NULL, null=True, blank=True, related_name="bills")
    payee = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=30, default="Due")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "payee"]


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    bill_to = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=30, default="Draft")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_methods")
    label = models.CharField(max_length=80)
    kind = models.CharField(max_length=30)
    masked_identifier = models.CharField(max_length=40)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "label"]


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=120)
    body = models.CharField(max_length=240)
    kind = models.CharField(max_length=30, default="info")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=80)
    key_prefix = models.CharField(max_length=20)
    status = models.CharField(max_length=30, default="Active")
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    phone = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=60, default="South Africa")
    verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    login_alerts = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)


class RewardEntry(models.Model):
    EARN = "earn"
    REDEEM = "redeem"
    ADJUST = "adjust"
    ACTIONS = [(EARN, "Earn"), (REDEEM, "Redeem"), (ADJUST, "Adjust")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reward_entries")
    action = models.CharField(max_length=8, choices=ACTIONS)
    points = models.PositiveIntegerField()
    description = models.CharField(max_length=140)
    status = models.CharField(max_length=30, default="Completed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class BankAccount(models.Model):
    TRANSACTION = "transaction"
    SAVINGS = "savings"
    ACCOUNT_TYPES = [(TRANSACTION, "Transactional"), (SAVINGS, "Savings")]
    ACTIVE = "active"
    FROZEN = "frozen"
    STATUSES = [(ACTIVE, "Active"), (FROZEN, "Frozen")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_accounts")
    name = models.CharField(max_length=80)
    account_number = models.CharField(max_length=24, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default=TRANSACTION)
    currency = models.CharField(max_length=3, default="ZAR")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUSES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    @property
    def masked_number(self):
        return f"•••• {self.account_number[-4:]}"


class BankCard(models.Model):
    PHYSICAL = "physical"
    VIRTUAL = "virtual"
    CARD_TYPES = [(PHYSICAL, "Physical"), (VIRTUAL, "Virtual")]
    ACTIVE = "active"
    FROZEN = "frozen"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    CARD_STATUSES = [(ACTIVE, "Active"), (FROZEN, "Frozen"), (BLOCKED, "Blocked"), (CANCELLED, "Cancelled")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_cards")
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="cards")
    label = models.CharField(max_length=60)
    card_type = models.CharField(max_length=10, choices=CARD_TYPES, default=PHYSICAL)
    last_four = models.CharField(max_length=4)
    status = models.CharField(max_length=10, choices=CARD_STATUSES, default=ACTIVE)
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    online_limit = models.DecimalField(max_digits=10, decimal_places=2, default=2500)
    pin_changed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class DebitOrder(models.Model):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    STATUSES = [(ACTIVE, "Active"), (PAUSED, "Paused"), (CANCELLED, "Cancelled")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="debit_orders")
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="debit_orders")
    payee = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    mandate_reference = models.CharField(max_length=80)
    next_date = models.DateField()
    status = models.CharField(max_length=12, choices=STATUSES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["next_date", "payee"]


class ServicePurchase(models.Model):
    AIRTIME = "airtime"
    LOTTO = "lotto"
    ELECTRICITY = "electricity"
    FINE = "fine"
    SERVICE_TYPES = [(AIRTIME, "Airtime"), (LOTTO, "Lottery ticket"), (ELECTRICITY, "Electricity"), (FINE, "Traffic fine")]
    DRAFT = "draft"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    STATUSES = [(DRAFT, "Draft"), (COMPLETED, "Completed"), (CANCELLED, "Cancelled")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_purchases")
    account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="service_purchases")
    service_type = models.CharField(max_length=16, choices=SERVICE_TYPES)
    recipient = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default=DRAFT)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_purchase")
    points_spent = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PaymentRequest(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    STATUSES = [(PENDING, "Pending"), (ACCEPTED, "Accepted"), (DECLINED, "Declined")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_requests")
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="payment_requests")
    requester = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=140)
    status = models.CharField(max_length=10, choices=STATUSES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
