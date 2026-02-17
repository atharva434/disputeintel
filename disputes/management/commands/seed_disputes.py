from django.core.management.base import BaseCommand
from disputes.models import DisputeCase, RiskAnalysis
import random
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds synthetic dispute data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        disputes = [
            ("I did not authorize this purchase at Wal-Mart.", 45.00, "Retail", "Unauthorized Transaction", "High"),
            ("Netflix charged me twice this month.", 15.99, "Digital Goods", "Duplicate Charge", "Low"),
            ("The hotel room was dirty and not as described.", 250.00, "Travel & Hospitality", "Merchant Dispute", "Medium"),
            ("I cancelled my subscription but was still charged.", 9.99, "Digital Goods", "Subscription Confusion", "Low"),
            ("Someone stole my card and bought a TV.", 800.00, "Retail", "Unauthorized Transaction", "High"),
            ("Food never arrived from Uber Eats.", 35.50, "Food & Beverage", "Merchant Dispute", "Medium"),
            ("I don't recognize this charge from 'SQ *Coffee Shop'.", 4.50, "Food & Beverage", "Unknown", "Low"),
            ("Refund was promised 10 days ago but never received.", 120.00, "Retail", "Refund Abuse", "Medium"),
            ("Mistakenly charged for annual plan instead of monthly.", 100.00, "Software", "Subscription Confusion", "Low"),
            ("Suspicious transaction in a country I have never visited.", 1200.00, "Travel & Hospitality", "Unauthorized Transaction", "High"),
        ]

        for desc, amount, category, classification, risk in disputes:
            case = DisputeCase.objects.create(
                description=desc,
                amount=amount,
                merchant_category=category,
                status='ANALYZED'
            )
            
            RiskAnalysis.objects.create(
                case=case,
                risk_score=risk,
                classification=classification,
                fraud_signals=["Simulated Signal 1", "Simulated Signal 2"] if risk == 'High' else [],
                reasoning_steps=["Step 1: Analyzed text", "Step 2: Checked amount", "Step 3: Assigned risk"],
                recommended_action="Manual Review" if risk == 'High' else "Auto Resolve"
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(disputes)} cases.'))
