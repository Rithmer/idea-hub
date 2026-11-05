from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_move_user_to_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='status',
            field=models.CharField(
                choices=[('не взята', 'Свободна'), ('взята', 'Взята')],
                default='не взята',
                help_text='Для взятой идеи укажите участника в поле «Выбрал».',
                max_length=10,
                verbose_name='Статус',
            ),
        ),
    ]
