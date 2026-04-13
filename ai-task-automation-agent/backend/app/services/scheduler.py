"""
Task scheduler - Schedule recurring tasks using APScheduler
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.models.database import SessionLocal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def cleanup_old_tasks():
    """Cleanup tasks older than 30 days"""
    db = SessionLocal()
    try:
        logger.info("Running scheduled task: cleanup_old_tasks")
        # Add your cleanup logic here
        pass
    except Exception as e:
        logger.error(f"Error in cleanup_old_tasks: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler with default jobs"""
    
    # Daily cleanup at 2 AM
    scheduler.add_job(
        cleanup_old_tasks,
        CronTrigger(hour=2, minute=0),
        id='daily_cleanup',
        name='Daily cleanup of old tasks',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✅ Task scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("👋 Task scheduler stopped")


def add_scheduled_job(func, cron_expression: str, job_id: str, name: str):
    """Add a custom scheduled job"""
    # Parse cron expression: minute hour day month day_of_week
    parts = cron_expression.split()
    scheduler.add_job(
        func,
        CronTrigger(
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4]
        ),
        id=job_id,
        name=name,
        replace_existing=True
    )
    logger.info(f"Added scheduled job: {name} ({cron_expression})")
