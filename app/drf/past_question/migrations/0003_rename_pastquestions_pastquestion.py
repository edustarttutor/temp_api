# Generated by Django 3.2 on 2021-11-08 22:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subject_related', '0003_auto_20210410_1232'),
        ('past_question', '0002_pastquestions_created_at'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PastQuestions',
            new_name='PastQuestion',
        ),
    ]
