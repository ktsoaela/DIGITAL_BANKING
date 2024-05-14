from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import UserAccount, Transaction
from decimal import Decimal

class UserAccountModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.account = UserAccount.objects.create(user=self.user, pin=1234, name='John', surname='Doe',
                                                  gender='Male', currency='USD', balance=1000)

    def test_account_creation(self):
        self.assertEqual(self.account.user.username, 'testuser')
        self.assertEqual(self.account.pin, 1234)
        self.assertEqual(self.account.name, 'John')
        self.assertEqual(self.account.surname, 'Doe')
        self.assertEqual(self.account.gender, 'Male')
        self.assertEqual(self.account.currency, 'USD')
        self.assertEqual(self.account.balance, 1000)


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.account = UserAccount.objects.create(user=self.user, pin=1234, name='John', surname='Doe',
                                                  gender='Male', currency='USD', balance=1000)

    def test_deposit_api(self):
        url = reverse('deposit')
        data = {'pin': 1234, 'amount': '500.00'}  
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserAccount.objects.get(pin=1234).balance, Decimal('1500.00'))

    def test_withdraw_api(self):
        url = reverse('withdraw')
        data = {'pin': 1234, 'amount': '300.00'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserAccount.objects.get(pin=1234).balance, Decimal('700.00'))

    def test_transaction_model(self):
        user = UserAccount.objects.get(pin=1234)
        Transaction.objects.create(user=user, transaction_type='deposit', amount=200)
        Transaction.objects.create(user=user, transaction_type='withdrawal', amount=100)
        self.assertEqual(Transaction.objects.count(), 2)
