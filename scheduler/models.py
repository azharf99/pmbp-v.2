# scheduler/models.py
from django.urls import reverse
from classes.models import Class
from courses.models import Course
from utils.choices import DAY_CHOICES
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Define choices for days of the week, excluding Friday
class Room(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g., 'Room 101', 'Science Lab'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse("timetable_view")
    

    class Meta:
        ordering = ["name"]
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")
        db_table = "rooms"
        indexes = [
            models.Index(fields=["id","name"]),
        ]

class Period(models.Model):
    number = models.PositiveIntegerField(unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Period {self.number} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    def get_absolute_url(self) -> str:
        return reverse("timetable_view")
    

    class Meta:
        ordering = ["number"]
        verbose_name = _("Period")
        verbose_name_plural = _("Periods")
        db_table = "periods"
        indexes = [
            models.Index(fields=["id", "number"]),
        ]

class Lesson(models.Model):
    """
    Represents a specific course that needs to be scheduled.
    This links a teacher, a subject, and a class.
    """
    subject_teacher = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='lessons')
    periods_per_week = models.PositiveIntegerField(default=1, help_text="Number of periods this lesson occurs per week (1-4).")
    consecutive_periods_needed = models.PositiveIntegerField(default=1, help_text="Number of consecutive periods for one session (e.g., 2 for a double period).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def get_absolute_url(self) -> str:
        return reverse("timetable_view")
    

    class Meta:
        unique_together = ('subject_teacher', 'class_assigned')
        ordering = ["subject_teacher", "class_assigned"]
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        db_table = "periods"
        indexes = [
            models.Index(fields=["id", "number"]),
        ]

    def clean(self):
        # Add validation to ensure consecutive periods make sense
        if self.consecutive_periods_needed > self.periods_per_week:
            raise ValidationError("Consecutive periods needed cannot be greater than total periods per week.")
        if self.periods_per_week % self.consecutive_periods_needed != 0:
            raise ValidationError("Periods per week should be divisible by the consecutive periods needed for simplicity.")

    def __str__(self):
        return f"{self.subject_teacher.course_name} for {self.class_assigned} by {self.subject_teacher.teacher}"

class TimetableEntry(models.Model):
    """
    A single, scheduled entry in the final timetable.
    This is the model that the generator will populate.
    """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ('day', 'period', 'subject_teacher'),
            ('day', 'period', 'room'),
            ('day', 'period', 'class_assigned'),
        )
        verbose_name_plural = "Timetable Entries"

    def __str__(self):
        return f"{self.lesson} in {self.room} on {self.day} at {self.period}"

    # We can add clean methods to add extra validation logic before saving.
    def clean(self):
        # Constraint: Teacher cannot be scheduled on their day off.
        if self.day == self.lesson.subject_teacher.teacher.day_off:
            raise ValidationError(f"Teacher {self.lesson.subject_teacher.teacher.teacher_name} has a day off on {self.day}.")

        # Constraint: No classes on Friday (already handled by DAY_CHOICES, but this is an extra safeguard).
        if self.day == "Friday":
            raise ValidationError("Scheduling on Friday is not allowed.")

    # We need to override the save method to dynamically get related fields
    # for the unique_together constraint check. To do this, we add proxy
    # fields that are not saved to the database.
    def save(self, *args, **kwargs):
        self.subject_teacher = self.lesson.subject_teacher
        self.class_assigned = self.lesson.class_assigned
        super().save(*args, **kwargs)

# Proxy fields for validation, not stored in the database
TimetableEntry.add_to_class('subject_teacher', models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True))
TimetableEntry.add_to_class('class_assigned', models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True))
