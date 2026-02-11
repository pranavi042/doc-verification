from django.db import models


class PanRecord(models.Model):
    name = models.CharField(max_length=100, default="UNKNOWN")
    father_name = models.CharField(max_length=100, default="UNKNOWN")
    pan_number = models.CharField(max_length=10, unique=True)
    dob = models.CharField(max_length=20, default="UNKNOWN")

    def __str__(self):
        return self.pan_number


class GstRecord(models.Model):
    gst_number = models.CharField(max_length=15, unique=True)
    legal_name = models.CharField(max_length=200, default="UNKNOWN")
    trade_name = models.CharField(max_length=200, default="UNKNOWN")

    def __str__(self):
        return self.gst_number


class CinRecord(models.Model):
    cin_number = models.CharField(max_length=30, unique=True)
    company_name = models.CharField(max_length=255, default="UNKNOWN")
    registration_date = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return self.cin_number
