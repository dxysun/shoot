# Generated by Django 2.0.3 on 2018-11-02 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shootweb', '0013_auto_20181030_1023'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GameInfo',
        ),
        migrations.DeleteModel(
            name='HeartRateData',
        ),
        migrations.DeleteModel(
            name='ItemAthleteRelation',
        ),
        migrations.DeleteModel(
            name='ItemCoachRelation',
        ),
        migrations.DeleteModel(
            name='ShakeBesideData',
        ),
        migrations.DeleteModel(
            name='ShakeUpData',
        ),
        migrations.DeleteModel(
            name='ShootData',
        ),
        migrations.DeleteModel(
            name='ShootItems',
        ),
        migrations.DeleteModel(
            name='StageInfo',
        ),
        migrations.DeleteModel(
            name='UserInfo',
        ),
    ]