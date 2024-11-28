from django.db import models
from django.utils import timezone

# Create your models here.
class FileReaderModel(models.Model):
    file = models.FileField()

    class Meta:
        verbose_name_plural = "FileReaderModel"