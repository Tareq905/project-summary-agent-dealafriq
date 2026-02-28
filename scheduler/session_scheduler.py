from apscheduler.schedulers.background import BackgroundScheduler
from services.session_data_builder import build_session_data
from services.unified_summary_builder import build_unified_summary

scheduler = BackgroundScheduler()

def run_job():

    for s in ["ONGOING","COMPLETED","CANCELLED"]:
        data = build_session_data(s)
        build_unified_summary(data)

scheduler.add_job(run_job,'interval',hours=1)