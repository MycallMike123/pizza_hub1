from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

EMAIL_FROM = 'no-reply@jobboard.com'

def send_verification_email(subject: str, email_to: list[str], html_template, context):
    """
    Send a verification email to the user.
    """
    msg = EmailMultiAlternatives(
        subject=subject, from_email=EMAIL_FROM, to=email_to
    )
    html_template = get_template(html_template)
    html_alternative = html_template.render(context)
    msg.attach_alternative(html_alternative, "text/html")
    msg.send(fail_silently=False)