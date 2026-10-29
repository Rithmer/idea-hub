"""Перенос состояния User в отдельное приложение без изменения таблицы."""
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="User",
                    fields=[
                        ("id", models.BigAutoField(
                            auto_created=True, primary_key=True, serialize=False, verbose_name="ID",
                        )),
                        ("name", models.CharField(max_length=150, unique=True, verbose_name="Имя")),
                        ("password", models.CharField(max_length=255, verbose_name="Хеш пароля")),
                        ("is_admin", models.BooleanField(default=False, verbose_name="Администратор")),
                    ],
                    options={
                        "db_table": "catalog_user",
                        "ordering": ("name", "pk"),
                        "verbose_name": "Участник",
                        "verbose_name_plural": "Участники",
                    },
                ),
            ],
        ),
    ]
