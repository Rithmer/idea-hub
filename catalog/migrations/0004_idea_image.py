from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_alter_idea_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='idea',
            name='image',
            field=models.ImageField(blank=True, upload_to='ideas/', verbose_name='Иллюстрация'),
        ),
    ]
