from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0003_atm_cash_proof")]
    operations = [
        migrations.CreateModel(
            name="Bill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payee", models.CharField(max_length=120)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("due_date", models.DateField()),
                ("status", models.CharField(default="Due", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bills", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["due_date", "payee"]},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("bill_to", models.CharField(max_length=120)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("issue_date", models.DateField()),
                ("due_date", models.DateField()),
                ("status", models.CharField(default="Draft", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoices", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PaymentMethod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=80)),
                ("kind", models.CharField(max_length=30)),
                ("masked_identifier", models.CharField(max_length=40)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payment_methods", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-is_default", "label"]},
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("body", models.CharField(max_length=240)),
                ("kind", models.CharField(default="info", max_length=30)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="APIKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("key_prefix", models.CharField(max_length=20)),
                ("status", models.CharField(default="Active", max_length=30)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="api_keys", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("country", models.CharField(default="South Africa", max_length=60)),
                ("verified", models.BooleanField(default=False)),
                ("two_factor_enabled", models.BooleanField(default=False)),
                ("login_alerts", models.BooleanField(default=True)),
                ("locked", models.BooleanField(default=False)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="customer_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
