from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Sets up specialist groups and users for testing routing logic'

    def handle(self, *args, **kwargs):
        # 1. Ensure Risk Ops group exists
        ops_group, _ = Group.objects.get_or_create(name='Risk Ops')
        
        # 2. Define Specialist Groups based on Classification
        specializations = [
            'Specialist: Unauthorized Transaction',
            'Specialist: Subscription Confusion',
            'Specialist: Refund Abuse',
            'Specialist: Merchandise Dispute'
        ]
        
        for name in specializations:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {name}"))
            else:
                self.stdout.write(f"Group exists: {name}")

        # 3. Create Test Users
        specialists = [
            ('ops_unauth', 'testpass123', 'Specialist: Unauthorized Transaction'),
            ('ops_sub', 'testpass123', 'Specialist: Subscription Confusion'),
            ('ops_refund', 'testpass123', 'Specialist: Refund Abuse'),
        ]
        
        for username, password, group_name in specialists:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.is_staff = True # Needed to access Ops Dashboard if using is_staff check
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
            
            # Add to generic Ops group AND Specialist group
            ops_group.user_set.add(user)
            
            spec_group = Group.objects.get(name=group_name)
            spec_group.user_set.add(user)
            
            self.stdout.write(f"Added {username} to {group_name}")

        self.stdout.write(self.style.SUCCESS("Specialist setup complete."))
