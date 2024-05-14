from django.contrib import admin
from .models import UserAccount, PINChange, Account, Transaction, CashWithdrawal, BalanceInquiry
from .models import Receipt, MiniStatement, Statement, BillPayment, MobileRecharge, PrepaidElectricityReload

admin.site.register(UserAccount)
admin.site.register(PINChange)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(CashWithdrawal)
admin.site.register(BalanceInquiry)
admin.site.register(Receipt)
admin.site.register(MiniStatement)
admin.site.register(Statement)
admin.site.register(BillPayment)
admin.site.register(MobileRecharge)
admin.site.register(PrepaidElectricityReload)
