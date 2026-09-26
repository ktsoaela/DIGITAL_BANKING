from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0002_banking_trading_models")]
    operations = [
        migrations.CreateModel(
            name="ATMTerminal",
            fields=[
                ("terminal_id", models.CharField(max_length=20, primary_key=True, serialize=False)),
                ("location", models.CharField(max_length=120)),
                ("status", models.CharField(default="Online", max_length=30)),
                ("cash_units", models.CharField(default="R50, R100, R200", max_length=120)),
                ("contactless", models.BooleanField(default=True)),
                ("cardless", models.BooleanField(default=True)),
            ],
            options={"ordering": ["terminal_id"]},
        ),
        migrations.CreateModel(
            name="CashTransfer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("direction", models.CharField(choices=[("withdrawal", "Withdrawal"), ("deposit", "Deposit"), ("send", "Cash send"), ("receive", "Cash receive")], max_length=10)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("recipient", models.CharField(blank=True, max_length=120)),
                ("reference", models.CharField(max_length=80)),
                ("status", models.CharField(default="Completed", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("terminal", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="dashboard.atmterminal")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cash_transfers", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ProofOfPayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("receipt_number", models.CharField(max_length=40, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("payment", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="proof", to="dashboard.payment")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proofs_of_payment", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
