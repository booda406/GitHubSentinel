from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.services.report_service import ReportService
from db.database import get_db

router = APIRouter()
report_service = ReportService()

@router.get("/reports/{repo_url}")
def get_report(repo_url: str, db: Session = Depends(get_db)):
    report = report_service.generate_report(repo_url)
    return {"report": report}
