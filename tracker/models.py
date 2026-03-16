from django.db import models


DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]

MUSCLE_GROUPS = [
    ('Chest', 'Chest'),
    ('Back', 'Back'),
    ('Shoulders', 'Shoulders'),
    ('Biceps', 'Biceps'),
    ('Triceps', 'Triceps'),
    ('Legs', 'Legs'),
    ('Glutes', 'Glutes'),
    ('Core / Abs', 'Core / Abs'),
    ('Full Body', 'Full Body'),
    ('Cardio', 'Cardio'),
    ('Other', 'Other'),
]


class WorkoutSession(models.Model):
    date = models.DateField()
    day = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    muscle_groups = models.CharField(max_length=200)  # comma-separated
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.day} - {self.muscle_groups}"

    def muscle_groups_list(self):
        return [m.strip() for m in self.muscle_groups.split(',') if m.strip()]


class Exercise(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class SetLog(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='sets')
    set_number = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    weight_unit = models.CharField(max_length=5, choices=[('kg', 'kg'), ('lbs', 'lbs')], default='kg')
    reps = models.PositiveIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['set_number']

    def __str__(self):
        return f"Set {self.set_number}: {self.weight}{self.weight_unit} x {self.reps}"
