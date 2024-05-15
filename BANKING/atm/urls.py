from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'user-accounts', views.UserAccountViewSet)
router.register(r'accounts', views.AccountViewSet)
router.register(r'balance-inquiries', views.BalanceInquiryViewSet)
router.register(r'pin-changes', views.PINChangeViewSet)

router.register(r'transactions', views.TransactionViewSet)
router.register(r'cash-withdrawals', views.CashWithdrawalViewSet)

router.register(r'receipts', views.ReceiptViewSet)
router.register(r'mini-statements', views.MiniStatementViewSet)
router.register(r'statements', views.StatementViewSet)

router.register(r'bill-payments', views.BillPaymentViewSet)
router.register(r'mobile-recharges', views.MobileRechargeViewSet)
router.register(r'prepaid-electricity-reloads', views.PrepaidElectricityReloadViewSet)

urlpatterns = [
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('api/', include(router.urls)), 
]

