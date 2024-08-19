from fastapi import FastAPI
from api.routers import subscriptions, updates, notifications, reports, github_info
from db.database import engine, Base
# from api.models import base

app = FastAPI(title="Github Sentinel")

# 創建數據庫表
Base.metadata.create_all(bind=engine)

# 註冊路由
app.include_router(subscriptions.router)
app.include_router(updates.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(github_info.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Github Sentinel"}
