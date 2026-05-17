from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import db
from app.api import characters, item_needs, dungeons, bosses, realms, gold, talents, exchange
from app.api.equipment import router as equipment_router
from app.api.character_refresh import router as refresh_router
from app.api.items import router as items_router
from app.api.settings import router as settings_router
from app.api.bis import router as bis_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="魔兽世界角色管理系统API"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=False,  # 使用*时不能为True
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """启动时连接数据库并创建表"""
    await db.connect()
    await db.init_tables()


@app.on_event("shutdown")
async def shutdown():
    """关闭时断开数据库连接"""
    await db.close()


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
        await db.fetchone("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


# 静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 注册路由
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(item_needs.router, prefix="/api/item-needs", tags=["item-needs"])
app.include_router(dungeons.router, prefix="/api/dungeons", tags=["dungeons"])
app.include_router(bosses.router, prefix="/api/bosses", tags=["bosses"])
app.include_router(realms.router, prefix="/api/realms", tags=["realms"])
app.include_router(gold.router, prefix="/api/gold", tags=["gold"])
app.include_router(talents.router, tags=["talents"])
app.include_router(equipment_router, tags=["equipment"])
app.include_router(refresh_router, prefix="/api/character-refresh", tags=["character-refresh"])
app.include_router(items_router, prefix="/api/items", tags=["items"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(bis_router, tags=["bis"])
app.include_router(exchange.router, prefix="/api/exchange", tags=["exchange"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
