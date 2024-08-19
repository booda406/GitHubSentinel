from .celery_app import celery_app
from api.services.github_service import GitHubService
from api.services.report_service import ReportService
from api.models.subscription import Subscription
from db.database import SessionLocal

@celery_app.task
def daily_update():
    db = SessionLocal()
    github_service = GitHubService()
    subscriptions = db.query(Subscription).all()
    
    for subscription in subscriptions:
        repo_info = github_service.get_repo_info(subscription.repo_url)
        # Update subscription or create a new update record
        # Implement notification logic here
    
    db.close()

@celery_app.task
def weekly_report():
    db = SessionLocal()
    report_service = ReportService()
    subscriptions = db.query(Subscription).all()
    
    for subscription in subscriptions:
        report = report_service.generate_report(subscription.repo_url)
        # Save report to database or send it to user
    
    db.close()
