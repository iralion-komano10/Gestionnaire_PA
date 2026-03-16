from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from pa.utils import check_and_send_reminders

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Planifier l'envoi tous les jours à 8h
    scheduler.add_job(
        check_and_send_reminders,
        trigger='cron',
        hour=8,
        minute=0,
        id='send_reminders',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Planificateur de rappels démarré")