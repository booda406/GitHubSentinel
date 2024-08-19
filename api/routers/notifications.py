from fastapi import APIRouter

router = APIRouter()

# 在這裡定義您的路由
@router.get("/notifications")
async def get_notifications():
    # 您的代碼邏輯
    pass
