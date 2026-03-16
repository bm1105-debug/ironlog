from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkoutSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('day', models.CharField(choices=[
                    ('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),
                    ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday'),
                ], max_length=20)),
                ('muscle_groups', models.CharField(max_length=200)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='sessions', to='auth.user')),
            ],
            options={'ordering': ['-date', '-created_at']},
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('order', models.PositiveIntegerField(default=0)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='exercises', to='tracker.workoutsession')),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='SetLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('set_number', models.PositiveIntegerField()),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('weight_unit', models.CharField(choices=[('kg','kg'),('lbs','lbs')], default='kg', max_length=5)),
                ('reps', models.PositiveIntegerField(blank=True, null=True)),
                ('notes', models.CharField(blank=True, max_length=200)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='sets', to='tracker.exercise')),
            ],
            options={'ordering': ['set_number']},
        ),
    ]
