from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import date, timedelta
from .models import PlanAction

def send_reminder_email(plan):
    """
    Envoie un email de rappel pour un plan dont l'échéance approche
    """
    subject = f'🔔 Rappel : Échéance du plan d\'action dans 1 jour'
    
    # Contexte pour le template
    context = {
        'plan': plan,
        'user': plan.user,
        'days_remaining': (plan.echeance - date.today()).days,
        'site_url': settings.SITE_URL  # À définir dans settings.py
    }
    
    # Template HTML
    html_message = render_to_string('pa/emails/reminder.html', context)
    plain_message = strip_tags(html_message)
    
    # Envoyer l'email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[plan.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    print(f"Email envoyé à {plan.user.email} pour le plan: {plan.description[:50]}")

def check_and_send_reminders():
    """
    Vérifie tous les plans et envoie des rappels pour ceux dont l'échéance est dans 1 jour
    """
    today = date.today()
    target_date = today + timedelta(days=1)
    
    # Plans dont l'échéance est demain et qui ne sont pas terminés ou annulés
    plans_a_rappeler = PlanAction.objects.filter(
        echeance=target_date,
        statut__in=['en_attente', 'en_cours'],  # Exclut terminé et annulé
    ).select_related('user')
    
    count = 0
    for plan in plans_a_rappeler:
        try:
            send_reminder_email(plan)
            count += 1
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email pour le plan {plan.id}: {e}")
    
    return count