from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from users.models import Teacher
from students.models import Student
from django.utils.translation import gettext as _


# Create your models here.
class Team(models.Model):
    team_leader = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, verbose_name=_("Ketua Tim"), related_name='team_leaders')
    members = models.ManyToManyField(Student, verbose_name=_("Anggota Tim"), related_name='teams', help_text=_("Ketik yang ingin dicari dan pilih. Kamu bisa memilih lebih dari 1 (satu). Untuk menghapusnya, klik nama yang ingin dihapus hingga berwarna biru/terang, lalu tekan delete atau backspace."))
    prev_members = models.TextField(_("Anggota Sebelumnya"), blank=True, null=True)
    status = models.CharField(_("Status Tim"), max_length=50, choices=(("Aktif", _("Aktif")), ("Tidak Aktif", _("Tidak Aktif"))), default="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Team {self.team_leader.student_name}"
    
    def get_absolute_url(self):
        return reverse('team-list')

    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        db_table = "teams"
        indexes = [
            models.Index(fields=["id",]),
        ]

class Project(models.Model):
    project_name = models.CharField(_("Nama Project"), max_length=255)
    start_date = models.DateField(_("Tanggal Mulai Project"), max_length=255)
    end_date = models.DateField(_("Tanggal Akhir Project"), max_length=255)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name=_("Pembimbing"))
    description = models.TextField(_("Deskripsi Project"), max_length=2000)
    step_to_achieve = models.TextField(_("Langkah Mencapai Project"), max_length=2000)
    task_organizing = models.TextField(_("Pembagian Tugas Project"), max_length=2000)
    slug = models.SlugField(max_length=255)
    semester = models.CharField(max_length=7, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN_LALU, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.project_name} - {self.team}"
    
    def get_absolute_url(self):
        return reverse('project-list')
    
    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.project_name}")
        super().save(*args, **kwargs)

    
    class Meta:
        ordering = ["-start_date", "project_name"]
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        db_table = "student_projects"
        indexes = [
            models.Index(fields=["id", "slug",]),
        ]


class DailyPlan(models.Model):
    date = models.DateField(_("Tanggal"), max_length=255)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, verbose_name=_("Nama Proyek"))
    to_do_list = models.TextField(_("List Pekerjaan Hari Ini"), max_length=2000)
    target_today = models.TextField(_("Target Hari ini"), max_length=2000)
    problems = models.TextField(_("Kendala yang dihadapi"), max_length=2000)
    semester = models.CharField(max_length=7, default=settings.SEMESTER, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} {self.project}"
    
    def get_absolute_url(self):
        return reverse('daily-plan-list')
    
    class Meta:
        ordering = ["-date"]
        verbose_name = _("Daily Plan")
        verbose_name_plural = _("Daily Plans")
        db_table = "daily_plans"
        indexes = [
            models.Index(fields=["id",]),
        ]