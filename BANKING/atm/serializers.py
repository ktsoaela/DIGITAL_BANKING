from rest_framework import serializers
from .models import UserAccount, PINChange, Account, Transaction, CashWithdrawal
from .models import BalanceInquiry, Receipt, MiniStatement, Statement, BillPayment
from .models import MobileRecharge, PrepaidElectricityReload


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = '__all__'


class PINChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PINChange
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class CashWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashWithdrawal
        fields = '__all__'


class BalanceInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceInquiry
        fields = '__all__'


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'


class MiniStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiniStatement
        fields = '__all__'


class StatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statement
        fields = '__all__'


class BillPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPayment
        fields = '__all__'


class MobileRechargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileRecharge
        fields = '__all__'


class PrepaidElectricityReloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepaidElectricityReload
        fields = '__all__'
