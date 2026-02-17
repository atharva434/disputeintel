from django.db import models

class Dataset(models.Model):
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Dataset {self.id} - {self.uploaded_at}"

class Report(models.Model):
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='report')
    profiling_data = models.JSONField(default=dict)
    anomaly_data = models.JSONField(default=dict)
    insights_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for Dataset {self.dataset.id}"
