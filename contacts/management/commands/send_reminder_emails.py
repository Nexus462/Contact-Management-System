"""
Management command to check for due reminders and send email notifications.
Run with: python manage.py send_reminder_emails
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from contacts.models import Contact
from datetime import timedelta


class Command(BaseCommand):
    help = 'Check for upcoming reminders and send email notifications'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find reminders due in the next 24 hours that haven't been sent yet
        upcoming_window = now + timedelta(hours=24)
        
        # Get all active reminders due soon
        due_reminders = Contact.objects.filter(
            has_reminder=True,
            reminder_date__lte=upcoming_window,
            reminder_date__gte=now
        ).select_related('user')
        
        sent_count = 0
        
        for contact in due_reminders:
            # Get user's email
            user_email = contact.user.email
            
            if not user_email:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping {contact.name} - user {contact.user.username} has no email'
                    )
                )
                continue
            
            # Calculate time until reminder
            time_until = contact.reminder_date - now
            hours_until = int(time_until.total_seconds() / 3600)
            minutes_until = int((time_until.total_seconds() % 3600) / 60)
            
            if hours_until > 0:
                time_str = f"{hours_until} hour{'s' if hours_until != 1 else ''}"
            else:
                time_str = f"{minutes_until} minute{'s' if minutes_until != 1 else ''}"
            
            # Prepare email content
            subject = f'⏰ Reminder: {contact.name}'
            
            message = f"""
Hello {contact.user.username},

This is a reminder about your contact: {contact.name}

📅 Reminder Time: {contact.reminder_date.strftime('%B %d, %Y at %I:%M %p')}
⏱️  Due in: {time_str}

Contact Details:
• Phone: {contact.phone}
• Email: {contact.email if contact.email else 'Not provided'}
"""
            
            if contact.reminder_note:
                message += f"• Note: {contact.reminder_note}\n"
            
            message += f"""
---
Manage this contact: http://127.0.0.1:8000/edit/{contact.pk}/

Best regards,
Contactify Team
"""
            
            try:
                # Send email
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    fail_silently=False,
                )
                
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Sent reminder for {contact.name} to {user_email}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to send email for {contact.name}: {str(e)}'
                    )
                )
        
        if sent_count == 0:
            self.stdout.write(
                self.style.WARNING('No reminders due in the next 24 hours')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully sent {sent_count} reminder email{"s" if sent_count != 1 else ""}'
                )
            )
