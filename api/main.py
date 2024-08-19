from fastapi import FastAPI
from api.routers import subscriptions, updates, notifications, reports
from db.database import engine
from api.models import base

app = FastAPI(title="Github Sentinel")

# 創建數據庫表
base.Base.metadata.create_all(bind=engine)

# 註冊路由
app.include_router(subscriptions.router)
app.include_router(updates.router)
app.include_router(notifications.router)
app.include_router(reports.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Github Sentinel"}
