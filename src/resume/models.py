from django.db import models


class Resume(models.Model):
    title = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    experience = models.TextField(max_length=200)
    education = models.TextField(max_length=200)
    s3_url = models.URLField(null=True, blank=True)

    class Meta:
        db_table = "resume"
