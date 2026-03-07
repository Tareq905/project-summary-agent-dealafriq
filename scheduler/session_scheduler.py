from apscheduler.schedulers.background import BackgroundScheduler
from services.session_data_builder import build_all_sessions_data
from services.intelligence_orchestrator import analyze_all_projects

scheduler = BackgroundScheduler()

def run_job():
    data = build_all_sessions_data()
    analyze_all_projects(data)

scheduler.add_job(run_job, 'interval', hours=1)