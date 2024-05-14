from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from decimal import Decimal
from .models import (
    UserAccount,
    PINChange,
    Account,
    Transaction,
    CashWithdrawal,
    BalanceInquiry,
    Receipt,
    MiniStatement,
    Statement,
    BillPayment,
    MobileRecharge,
    PrepaidElectricityReload,
)
from .serializers import (
    UserAccountSerializer,
    PINChangeSerializer,
    AccountSerializer,
    TransactionSerializer,
    CashWithdrawalSerializer,
    BalanceInquirySerializer,
    ReceiptSerializer,
    MiniStatementSerializer,
    StatementSerializer,
    BillPaymentSerializer,
    MobileRechargeSerializer,
    PrepaidElectricityReloadSerializer,
)


def deposit(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        amount = float(request.POST.get('amount', 0))

        try:
            account = get_object_or_404(UserAccount, pin=pin)
        except UserAccount.DoesNotExist:
            return JsonResponse({"error": "Invalid PIN."}, status=400)

        if amount <= 0:
            return JsonResponse({"error": "Invalid deposit amount."}, status=400)

        if account.deposit(amount):
            return JsonResponse({
                "message": f"Successfully deposited ${amount}. New balance: ${account.balance}"
            })
        else:
            return JsonResponse({"error": "Deposit operation failed."}, status=400)

    return render(request, 'deposit.html')


def withdraw(request):
    if request.method == 'POST':
        pin = request.POST.get('pin')
        amount = float(request.POST.get('amount', 0))

        try:
            account = get_object_or_404(UserAccount, pin=pin)
        except UserAccount.DoesNotExist:
            return JsonResponse({"error": "Invalid PIN."}, status=400)

        if amount <= 0:
            return JsonResponse({"error": "Invalid withdrawal amount."}, status=400)

        if account.withdraw(amount):
            return JsonResponse({
                "message": f"Withdrew ${amount}. New balance: ${account.balance}"
            })
        else:
            return JsonResponse({"error": "Insufficient funds or withdrawal failed."}, status=400)

    return render(request, 'withdraw.html')


class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer

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

class PINChangeViewSet(viewsets.ModelViewSet):
    queryset = PINChange.objects.all()
    serializer_class = PINChangeSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class CashWithdrawalViewSet(viewsets.ModelViewSet):
    queryset = CashWithdrawal.objects.all()
    serializer_class = CashWithdrawalSerializer


class BalanceInquiryViewSet(viewsets.ModelViewSet):
    queryset = BalanceInquiry.objects.all()
    serializer_class = BalanceInquirySerializer


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer


class MiniStatementViewSet(viewsets.ModelViewSet):
    queryset = MiniStatement.objects.all()
    serializer_class = MiniStatementSerializer


class StatementViewSet(viewsets.ModelViewSet):
    queryset = Statement.objects.all()
    serializer_class = StatementSerializer


class BillPaymentViewSet(viewsets.ModelViewSet):
    queryset = BillPayment.objects.all()
    serializer_class = BillPaymentSerializer


class MobileRechargeViewSet(viewsets.ModelViewSet):
    queryset = MobileRecharge.objects.all()
    serializer_class = MobileRechargeSerializer


class PrepaidElectricityReloadViewSet(viewsets.ModelViewSet):
    queryset = PrepaidElectricityReload.objects.all()
    serializer_class = PrepaidElectricityReloadSerializer
