"""Начальная миграция участников, идей, связей и ограничений."""


import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taxonomy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID',
                )),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Имя')),
                ('password', models.CharField(max_length=255, verbose_name='Хеш пароля')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Администратор')),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
                'ordering': ('name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID',
                )),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('status', models.CharField(
                    choices=[('не взята', 'Свободна'), ('взята', 'Взята')],
                    default='не взята', max_length=10, verbose_name='Статус',
                )),
                ('created_at', models.DateField(
                    default=django.utils.timezone.localdate, verbose_name='Дата создания',
                )),
                ('category', models.ForeignKey(

                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='ideas', to='taxonomy.category', verbose_name='Категория',
                )),
                ('author', models.ForeignKey(

                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='authored_ideas', to='catalog.user', verbose_name='Автор',
                )),
                ('selected_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='selected_ideas', to='catalog.user', verbose_name='Выбрал',
                )),
            ],
            options={
                'verbose_name': 'Идея',
                'verbose_name_plural': 'Идеи',
                'ordering': ('-created_at', '-pk'),
                'indexes': [models.Index(fields=['status', 'created_at'], name='idea_status_date')],
                'constraints': [
                    models.CheckConstraint(
                        condition=(models.Q(selected_by__isnull=True, status='не взята')
                                   | models.Q(selected_by__isnull=False, status='взята')),
                        name='idea_status_selection_consistent',
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(selected_by__isnull=False), fields=('selected_by',),
                        name='one_selected_idea_per_user',
                    ),
                ],
            },
        ),
    ]
