# Generated by Django 3.2.17 on 2024-02-24 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20240224_1525'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Nota',
            new_name='Notas',
        ),
        migrations.AddField(
            model_name='tiposcurso',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.empresas'),
        ),
    ]
