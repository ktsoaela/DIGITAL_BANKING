from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("beneficiary", models.CharField(max_length=120)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("reference", models.CharField(max_length=140)),
                ("status", models.CharField(default="Submitted", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=140)),
                ("category", models.CharField(default="Everyday", max_length=60)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("direction", models.CharField(choices=[("credit", "Credit"), ("debit", "Debit")], max_length=6)),
                ("status", models.CharField(default="Completed", max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
