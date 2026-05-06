from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import db
from app.api import characters, item_needs, dungeons, bosses, realms

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="魔兽世界角色管理系统API"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    """启动时连接数据库"""
    await db.connect_to_database()


@app.on_event("shutdown")
async def shutdown_db_client():
    """关闭时断开数据库连接"""
    await db.close_database_connection()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to WoW Character Manager API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        await db.get_database().command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


# 注册路由
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(item_needs.router, prefix="/api/item-needs", tags=["item-needs"])
app.include_router(dungeons.router, prefix="/api/dungeons", tags=["dungeons"])
app.include_router(bosses.router, prefix="/api/bosses", tags=["bosses"])
app.include_router(realms.router, prefix="/api/realms", tags=["realms"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)