from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("dashboard", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Beneficiary",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("account_identifier", models.CharField(max_length=80)),
                ("bank_label", models.CharField(default="KHOEBO account", max_length=80)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="beneficiaries", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Instrument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("symbol", models.CharField(max_length=12, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("day_change", models.DecimalField(decimal_places=2, max_digits=6)),
                ("currency", models.CharField(default="ZAR", max_length=3)),
            ],
            options={"ordering": ["symbol"]},
        ),
        migrations.CreateModel(
            name="Pocket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=60)),
                ("target_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("rate", models.DecimalField(decimal_places=2, default=5, max_digits=5)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pockets", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="TradeOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("side", models.CharField(choices=[("buy", "Buy"), ("sell", "Sell")], max_length=4)),
                ("quantity", models.PositiveIntegerField()),
                ("limit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(default="Queued", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("instrument", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="dashboard.instrument")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trade_orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="WatchlistItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("instrument", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="watchers", to="dashboard.instrument")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="watchlist", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["instrument__symbol"], "constraints": [models.UniqueConstraint(fields=("user", "instrument"), name="unique_user_watchlist_instrument")]},
        ),
    ]
