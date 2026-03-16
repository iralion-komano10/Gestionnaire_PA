# pa/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from pa.utils import check_and_send_reminders
import logging

logger = logging.getLogger(__name__)

def start_scheduler():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        scheduler.add_job(
            check_and_send_reminders,
            trigger='cron',
            hour=8,
            minute=0,
            id='send_reminders_daily',
            replace_existing=True,
        )
        
        scheduler.start()
        logger.info("✅ Planificateur démarré")
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")