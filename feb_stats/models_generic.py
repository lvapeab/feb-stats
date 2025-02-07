from django.db import models

from feb_stats.constants import LARGE_CHAR_FIELD_SIZE


class DateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = ["created_at"]


class ExidModel(models.Model):
    exid = models.CharField(
        max_length=LARGE_CHAR_FIELD_SIZE,
        unique=True,
        editable=False,
    )

    class Meta:
        abstract = True
