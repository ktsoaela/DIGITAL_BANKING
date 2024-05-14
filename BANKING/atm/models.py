from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import pycountry
from decimal import Decimal

class UserAccount(models.Model):
    LANGUAGES = [(lang.alpha_3, lang.name) for lang in pycountry.languages]
    
    CURRENCIES = [(currency.alpha_3, currency.name) for currency in pycountry.currencies]


    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pin = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='ZAR')
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_card_activated = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=3, choices=LANGUAGES, default='en')

    def activate_card(self):
        self.is_card_activated = True
        self.save()

    def __str__(self):
        return f"{self.name} {self.surname}"

    def deposit(self, amount):
        if amount > Decimal('0'):
            self.balance += Decimal(str(amount))
            self.save()
            Transaction.objects.create(user=self, transaction_type='deposit', amount=amount)
            return True
        return False

    def withdraw(self, amount):
        if amount > Decimal('0') and self.balance >= Decimal(str(amount)):
            self.balance -= Decimal(str(amount))
            self.save()
            Transaction.objects.create(user=self, transaction_type='withdrawal', amount=amount)
            return True
        return False


class PINChange(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    new_pin = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PIN change for {self.user.name} on {self.timestamp}"


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('notice_deposit', 'Notice Deposit Account'),
        ('fixed_deposit', 'Fixed Deposit Account'),
        ('money_market', 'Money Market Account'),
        ('investment', 'Investment Account'),
        ('transactional', 'Transactional Account'),
        ('foreign_currency', 'Foreign Currency Account'),
        ('student', 'Student Account'),
        ('business', 'Business Account'),
        ('trust', 'Trust Account'),
        ('credit_card', 'Credit Card Account'),
        ('home_loan', 'Home Loan Account'),
        ('retirement', 'Retirement Account'),
    ]

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.name}'s {self.get_account_type_display()}"

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.save()
            Transaction.objects.create(account=self, transaction_type='deposit', amount=amount)
            return True
        return False

    def withdraw(self, amount):
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.save()
            Transaction.objects.create(account=self, transaction_type='withdrawal', amount=amount)
            return True
        return False

class Transaction(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')])
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ${self.amount} by {self.user} on {self.timestamp}"


class CashWithdrawal(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal of ${self.amount} by {self.user.name} on {self.timestamp}"


class BalanceInquiry(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Balance inquiry by {self.user.name} on {self.timestamp}"


class Receipt(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for {self.transaction_type} of ${self.amount} by {self.user.name} at {self.transaction_timestamp}"


class MiniStatement(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mini statement for {self.user.name} on {self.timestamp}"

class StatementDuration(models.IntegerChoices):
    MINI = 1, 'Mini Statement (Last 7 Days)'
    THIRTY_DAYS = 30, 'Last 30 Days Statement'
    NINETY_DAYS = 90, 'Last 90 Days Statement'
    ONE_TWENTY_DAYS = 120, 'Last 120 Days Statement'

class Statement(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    duration = models.PositiveSmallIntegerField(choices=StatementDuration.choices)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Statement for {self.user.name} - {self.get_duration_display()}"



class BillPayment(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    biller_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} paid {self.biller_name} ${self.amount} on {self.transaction_timestamp}"


class MobileRecharge(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} recharged {self.mobile_number} with ${self.amount} on {self.transaction_timestamp}"


class PrepaidElectricityReload(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} reloaded prepaid electricity card {self.card_number} with ${self.amount} on {self.transaction_timestamp}"
