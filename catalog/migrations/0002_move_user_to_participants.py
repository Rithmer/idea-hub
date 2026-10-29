"""Переключение связей на participants.User с сохранением таблиц и данных."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
        ("participants", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="idea",
                    name="author",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="authored_ideas", to="participants.user", verbose_name="Автор",
                    ),
                ),
                migrations.AlterField(
                    model_name="idea",
                    name="selected_by",
                    field=models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                        related_name="selected_ideas", to="participants.user", verbose_name="Выбрал",
                    ),
                ),
                migrations.DeleteModel(name="User"),
            ],
        ),
    ]
