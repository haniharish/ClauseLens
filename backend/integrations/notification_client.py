"""
ClauseLens – Notification / Email Client.

Wraps Django's email backend.
Email is DISABLED in development unless EMAIL_BACKEND is set
to a real SMTP backend in .env.

Usage:
    from integrations.notification_client import send_alert_email
    send_alert_email(user, notification)
"""
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger('clauselens')


def send_alert_email(user, notification) -> bool:
    """
    Send an email notification to the user about a policy change.
    Returns True if the email was sent (or queued), False otherwise.
    Only sends if EMAIL_HOST is configured.
    """
    if not settings.EMAIL_HOST:
        logger.debug('Email not configured. Skipping email to %s.', user.email)
        return False

    try:
        send_mail(
            subject=f'[ClauseLens] {notification.title}',
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info('Alert email sent to %s for notification %d', user.email, notification.id)
        return True
    except Exception as exc:
        logger.error('Failed to send email to %s: %s', user.email, exc)
        return False
