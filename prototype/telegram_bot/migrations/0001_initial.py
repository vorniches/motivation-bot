# Generated by Django 4.2.2 on 2025-01-19 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('task_type', models.CharField(choices=[('self_help', 'Self-help Coach'), ('text_task', 'Text Task'), ('mindfulness', 'Mindfulness and Gratitude'), ('brain_train', 'Brain-train')], max_length=20)),
                ('task_content', models.TextField()),
                ('user_response', models.TextField(blank=True, null=True)),
                ('is_correct', models.BooleanField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
