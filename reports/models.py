from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from schedules.models import Period, Schedule
from datetime import datetime
from users.models import Teacher
from utils.constants import GENDER_CHOICES, STATUS_CHOICES, WEEKDAYS


class Report(models.Model):
    report_date = models.DateField(_("Tanggal"))
    report_day = models.CharField(_("Hari"), max_length=20, blank=True, help_text=_("Opsional. Auto-generated"))
    duty = models.TextField(_("Tugas"), max_length=250, blank=True, null=True, help_text=_("Opsional. Jika ada"))
    notes = models.TextField(_("Keterangan"), max_length=250, blank=True, null=True, help_text=_("Opsional. Jika ada"))
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, related_name='reports', null=True, verbose_name=_("Jadwal"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[1][0])
    subtitute_teacher = models.ForeignKey(Teacher, related_name="subtitute_teacher", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Guru Pengganti"))
    reporter = models.ForeignKey(Teacher, related_name="reporter", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Petugas Piket"))
    is_submitted = models.BooleanField("Sudah di-submit?", default=False)
    is_complete = models.BooleanField("Sudah complete", default=False)
    semester = models.CharField(max_length=7, default=settings.SEMESTER, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN, blank=True, null=True)
    type = models.CharField(_("Tipe"), max_length=20, choices=GENDER_CHOICES, default=GENDER_CHOICES[1][0])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def report_day(self):
        return WEEKDAYS.get(self.report_date.weekday(), "Error")

    def __str__(self) -> str:
        return F"{self.report_date.strftime('%Y-%m-%d')} | {self.status} | {self.schedule}"
    

    def get_absolute_url(self) -> str:
        return reverse("report-list")
    

    class Meta:
        unique_together = (
            ('report_date', 'schedule'),
            ('report_date', 'schedule', 'type', 'semester', 'academic_year'),
        )
        ordering = ["-report_date", "schedule__schedule_class", "schedule__schedule_time"]
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        db_table = "class_reports"
        indexes = [
            models.Index(fields=["report_date"]),
        ]


class NonTeacherReport(models.Model):
    teacher = models.ForeignKey(Teacher, related_name="nonteachers", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Nama"))
    report_date = models.DateField(_("Tanggal"))
    report_day = models.CharField(_("Hari"), max_length=20, blank=True, help_text=_("Opsional. Auto-generated"))
    schedule_time = models.ForeignKey(Period, on_delete=models.SET_NULL, related_name='nonteachers', null=True, verbose_name=_("Jam ke-"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[1][0])
    notes = models.TextField(_("Keterangan"), max_length=250, blank=True, null=True, help_text=_("Opsional. Jika ada"))
    is_submitted = models.BooleanField("Sudah di-submit?", default=False)
    is_complete = models.BooleanField("Sudah complete", default=False)
    semester = models.CharField(max_length=7, default=settings.SEMESTER, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN, blank=True, null=True)
    type = models.CharField(_("Tipe"), max_length=20, choices=GENDER_CHOICES, default=GENDER_CHOICES[1][0])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def report_day(self):
        return WEEKDAYS.get(self.report_date.weekday(), "Error")
    

    def __str__(self) -> str:
        return F"{self.teacher} |{self.report_date.strftime('%Y-%m-%d')} | {self.status} | {self.schedule_time}"
    

    def get_absolute_url(self) -> str:
        return reverse("report-non-teacher-list")
    

    class Meta:
        unique_together = (
            ('report_date', 'teacher', 'schedule_time'),
            ('report_date', 'teacher', 'schedule_time', 'type', 'semester', 'academic_year'),
        )
        ordering = ["-report_date", "schedule_time", "teacher__teacher_name"]
        verbose_name = _("Non Teacher Report")
        verbose_name_plural = _("Non Teacher Reports")
        db_table = "non_teacher_reports"
        indexes = [
            models.Index(fields=["report_date"]),
        ]