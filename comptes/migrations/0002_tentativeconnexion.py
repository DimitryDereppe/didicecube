from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TentativeConnexion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cle', models.CharField(max_length=64, unique=True)),
                ('echecs', models.PositiveIntegerField(default=0)),
                ('bloque_jusqua', models.DateTimeField(blank=True, null=True)),
                ('derniere', models.DateTimeField(db_index=True)),
            ],
            options={
                'verbose_name': 'tentative de connexion',
                'verbose_name_plural': 'tentatives de connexion',
            },
        ),
    ]
