from django.db import models
from django.contrib.auth.models import User

class DisputeCase(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('ANALYZED', 'Analyzed'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    # Core Fields
    description = models.TextField(help_text="The dispute description text")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Transaction amount")
    merchant_category = models.CharField(max_length=100, help_text="e.g., Software, Retail, Travel")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # User Relations
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes', null=True, blank=True)
    assigned_ops = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_cases', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Case #{self.id} - {self.merchant_category} (${self.amount})"

class RiskAnalysis(models.Model):
    case = models.OneToOneField(DisputeCase, on_delete=models.CASCADE, related_name='analysis')
    risk_score = models.CharField(max_length=20, help_text="Low, Medium, High")
    classification = models.CharField(max_length=100, help_text="Dispute reason classification")
    fraud_signals = models.JSONField(default=list, help_text="List of detected fraud indicators")
    reasoning_steps = models.JSONField(default=list, help_text="Step-by-step reasoning logic")
    recommended_action = models.CharField(max_length=255, help_text="Suggested next step")
    financial_exposure = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Risk Analysis for Case #{self.case.id}"

class DisputeChatMessage(models.Model):
    case = models.ForeignKey(DisputeCase, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_internal_note = models.BooleanField(default=False, help_text="If True, visible only to Ops team")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender} on Case #{self.case.id}"
