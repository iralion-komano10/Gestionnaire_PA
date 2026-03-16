# pa/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from pa.utils import check_and_send_reminders
from datetime import date, timedelta
from pa.models import PlanAction

class Command(BaseCommand):
    help = 'Envoie des rappels par email pour les plans arrivant à échéance'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule l\'envoi sans réellement envoyer les emails',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Vérification des échéances...'))
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Mode DRY RUN - Aucun email ne sera envoyé'))
            plans = PlanAction.objects.filter(
                echeance=date.today() + timedelta(days=1),
                statut__in=['en_attente', 'en_cours']
            )
            self.stdout.write(f"📊 {plans.count()} plan(s) auraient reçu un rappel")
            return
        
        count = check_and_send_reminders()
        
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ {count} rappel(s) envoyé(s) avec succès'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️ Aucun rappel à envoyer aujourd\'hui'))