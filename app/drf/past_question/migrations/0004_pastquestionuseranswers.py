# Generated by Django 3.2 on 2021-11-09 01:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('past_question', '0003_rename_pastquestions_pastquestion'),
    ]

    operations = [
        migrations.CreateModel(
            name='PastQuestionUserAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_taken_on', models.DateField(auto_now_add=True)),
                ('test_type', models.CharField(choices=[('obj', 'obj'), ('theory', 'theory'), ('alternative-theory', 'alternative-theory')], max_length=250)),
                ('time_estimate', models.TimeField()),
                ('score', models.IntegerField(blank=True, default=0, null=True)),
                ('overall_score', models.IntegerField(blank=True, null=True)),
                ('questions_answers', models.JSONField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
