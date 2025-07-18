from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse

from utils.models import CleanableFileModel


# Create your models here.
class File(CleanableFileModel):
    file = models.FileField(upload_to='files', verbose_name=_("Upload File"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.file}"
    
    file_field_names = ['file']
    

    def get_absolute_url(self):
        return reverse("file-list")
    

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("File")
        verbose_name_plural = _("Files")
        db_table = "files"
        indexes = [
            models.Index(fields=["id",]),
        ]