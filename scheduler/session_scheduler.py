from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import logging

from services.session_data_builder import build_session_data
from services.intelligence_orchestrator import (
    analyze_all_projects,
    analyze_all_meetings,
    analyze_all_documents,
)
from services.email_orchestrator import analyze_all_emails
from services.client_orchestrator import analyze_all_clients

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_all_agents():
    logger.info("🤖 Scheduler triggered: Starting full AI analysis...")
    try:
        data = build_session_data()
        logger.info("📊 Running Project Analysis...")
        analyze_all_projects(data)
        logger.info("🗓️ Running Meeting Analysis...")
        analyze_all_meetings(data)
        logger.info("📄 Running Document Analysis...")
        analyze_all_documents(data)
        logger.info("📧 Running Email Analysis...")
        analyze_all_emails()
        logger.info("👤 Running Client Analysis...")
        analyze_all_clients()
        logger.info("✅ Scheduler: Full AI analysis complete.")
    except Exception as e:
        logger.error(f"💥 Scheduler job failed: {e}", exc_info=True)


def run_project_only():
    logger.info("🤖 Scheduler triggered: Project-only analysis...")
    try:
        data = build_session_data()
        analyze_all_projects(data)
        logger.info("✅ Scheduler: Project analysis complete.")
    except Exception as e:
        logger.error(f"💥 Project scheduler failed: {e}", exc_info=True)


def run_meeting_only():
    logger.info("🤖 Scheduler triggered: Meeting-only analysis...")
    try:
        data = build_session_data()
        analyze_all_meetings(data)
        logger.info("✅ Scheduler: Meeting analysis complete.")
    except Exception as e:
        logger.error(f"💥 Meeting scheduler failed: {e}", exc_info=True)


def run_document_only():
    logger.info("🤖 Scheduler triggered: Document-only analysis...")
    try:
        data = build_session_data()
        analyze_all_documents(data)
        logger.info("✅ Scheduler: Document analysis complete.")
    except Exception as e:
        logger.error(f"💥 Document scheduler failed: {e}", exc_info=True)


def run_email_only():
    logger.info("🤖 Scheduler triggered: Email-only analysis...")
    try:
        analyze_all_emails()
        logger.info("✅ Scheduler: Email analysis complete.")
    except Exception as e:
        logger.error(f"💥 Email scheduler failed: {e}", exc_info=True)


def run_client_only():
    logger.info("🤖 Scheduler triggered: Client-only analysis...")
    try:
        analyze_all_clients()
        logger.info("✅ Scheduler: Client analysis complete.")
    except Exception as e:
        logger.error(f"💥 Client scheduler failed: {e}", exc_info=True)


def start_scheduler():
    if scheduler.running:
        logger.info("⚠️ Scheduler already running. Skipping start.")
        return

    # 1. Full analysis — every 1 hour
    scheduler.add_job(
        run_all_agents,
        trigger=IntervalTrigger(hours=1),
        id="full_analysis",
        name="Full AI Analysis (Hourly)",
        replace_existing=True
    )

    # 2. Project only — every 30 minutes
    scheduler.add_job(
        run_project_only,
        trigger=IntervalTrigger(minutes=30),
        id="project_analysis",
        name="Project Analysis (Every 30 min)",
        replace_existing=True
    )

    # 3. Meeting only — every 30 minutes
    scheduler.add_job(
        run_meeting_only,
        trigger=IntervalTrigger(minutes=30),
        id="meeting_analysis",
        name="Meeting Analysis (Every 30 min)",
        replace_existing=True
    )

    # 4. Document only — every 30 minutes
    scheduler.add_job(
        run_document_only,
        trigger=IntervalTrigger(minutes=30),
        id="document_analysis",
        name="Document Analysis (Every 30 min)",
        replace_existing=True
    )

    # 5. Email only — every 15 minutes
    scheduler.add_job(
        run_email_only,
        trigger=IntervalTrigger(minutes=15),
        id="email_analysis",
        name="Email Analysis (Every 15 min)",
        replace_existing=True
    )

    # 6. Client only — every 1 hour
    scheduler.add_job(
        run_client_only,
        trigger=IntervalTrigger(hours=1),
        id="client_analysis",
        name="Client Analysis (Every 1 hour)",
        replace_existing=True
    )

    # 7. Daily full reset — every midnight
    scheduler.add_job(
        run_all_agents,
        trigger=CronTrigger(hour=0, minute=0),
        id="daily_full_reset",
        name="Daily Full Analysis (Midnight)",
        replace_existing=True
    )

    scheduler.start()
    logger.info("✅ Scheduler started successfully.")
    logger.info("📅 Jobs scheduled:")
    logger.info("   • Full Analysis     → Every 1 hour")
    logger.info("   • Project Analysis  → Every 30 minutes")
    logger.info("   • Meeting Analysis  → Every 30 minutes")
    logger.info("   • Document Analysis → Every 30 minutes")
    logger.info("   • Email Analysis    → Every 15 minutes")
    logger.info("   • Client Analysis   → Every 1 hour")
    logger.info("   • Daily Full Reset  → Every midnight")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Scheduler stopped.")