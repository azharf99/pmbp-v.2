from django.db import models

class CleanableFileModel(models.Model):
    """
    Abstract base model to automatically clean up old files
    when a file field is updated or when the instance is deleted.
    """
    file_field_names = []  # Must be set in child models

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            old = type(self).objects.filter(pk=self.pk).first()
            if old:
                for field in self.file_field_names:
                    old_file = getattr(old, field)
                    new_file = getattr(self, field)

                    if old_file and old_file != new_file:
                        if old_file.storage.exists(old_file.name):
                            old_file.storage.delete(old_file.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for field in self.file_field_names:
            file = getattr(self, field)
            if file and file.storage.exists(file.name):
                file.storage.delete(file.name)
        super().delete(*args, **kwargs)
