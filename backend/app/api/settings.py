"""
系统配置API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os

from app.core.config import settings as app_settings

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsRequest(BaseModel):
    accountantPath: Optional[str] = ""
    tdinspectPath: Optional[str] = ""
    atlaslootPath: Optional[str] = ""


class SettingsResponse(BaseModel):
    accountantPath: str = ""
    tdinspectPath: str = ""
    atlaslootPath: str = ""
    # 数据库中的原始配置
    dbAccountantPath: Optional[str] = None
    dbTdinspectPath: Optional[str] = None
    dbAtlaslootPath: Optional[str] = None
    # 默认配置
    defaultAccountantPath: str = ""
    defaultTdinspectPath: str = ""
    defaultAtlaslootPath: str = ""


class StatsResponse(BaseModel):
    characters: int = 0
    dungeons: int = 0
    bosses: int = 0
    items: int = 0


def get_db():
    conn = sqlite3.connect(app_settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
async def get_settings(includeSource: bool = False):
    """获取系统配置（合并数据库配置和默认配置）"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查是否存在settings表
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='settings'
    """)
    if not cursor.fetchone():
        # 创建设置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
    
    # 获取数据库中的设置
    cursor.execute("SELECT key, value FROM settings")
    db_settings = {row['key']: row['value'] for row in cursor.fetchall()}
    conn.close()
    
    # 合并后的配置（数据库配置优先）
    merged = {
        'accountantPath': db_settings.get('accountant_path') or settings.DEFAULT_ACCOUNTANT_PATH,
        'tdinspectPath': db_settings.get('tdinspect_path') or settings.DEFAULT_TDINSPECT_PATH,
        'atlaslootPath': db_settings.get('atlasloot_path') or settings.DEFAULT_ATLASLOOT_PATH
    }
    
    # 如果需要返回配置来源详情
    if includeSource:
        merged['dbAccountantPath'] = db_settings.get('accountant_path')
        merged['dbTdinspectPath'] = db_settings.get('tdinspect_path')
        merged['dbAtlaslootPath'] = db_settings.get('atlasloot_path')
        merged['defaultAccountantPath'] = settings.DEFAULT_ACCOUNTANT_PATH
        merged['defaultTdinspectPath'] = settings.DEFAULT_TDINSPECT_PATH
        merged['defaultAtlaslootPath'] = settings.DEFAULT_ATLASLOOT_PATH
    
    return merged


@router.post("")
async def save_settings(settings: SettingsRequest):
    """保存系统配置"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 确保表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # 保存设置
    settings_data = [
        ('accountant_path', settings.accountantPath),
        ('tdinspect_path', settings.tdinspectPath),
        ('atlasloot_path', settings.atlaslootPath)
    ]
    
    for key, value in settings_data:
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))
    
    conn.commit()
    conn.close()
    
    return {"message": "设置保存成功"}


@router.get("/test")
async def test_connections():
    """测试数据源连接"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取设置
    cursor.execute("SELECT key, value FROM settings WHERE key IN (?, ?, ?)",
                   ('accountant_path', 'tdinspect_path', 'atlasloot_path'))
    settings = {row['key']: row['value'] for row in cursor.fetchall()}
    conn.close()
    
    results = {
        "accountant": {"exists": False, "path": settings.get('accountant_path', '')},
        "tdinspect": {"exists": False, "path": settings.get('tdinspect_path', '')},
        "atlasloot": {"exists": False, "path": settings.get('atlasloot_path', '')}
    }
    
    # 检查文件/目录是否存在
    if results["accountant"]["path"] and os.path.exists(results["accountant"]["path"]):
        results["accountant"]["exists"] = True
    
    if results["tdinspect"]["path"] and os.path.exists(results["tdinspect"]["path"]):
        results["tdinspect"]["exists"] = True
    
    if results["atlasloot"]["path"] and os.path.exists(results["atlasloot"]["path"]):
        results["atlasloot"]["exists"] = True
    
    all_exist = all(r["exists"] for r in results.values() if r["path"])
    
    return {
        "success": all_exist,
        "results": results
    }


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取数据统计"""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = StatsResponse()
    
    # 角色数量
    cursor.execute("SELECT COUNT(*) FROM characters")
    stats.characters = cursor.fetchone()[0]
    
    # 副本数量
    cursor.execute("SELECT COUNT(*) FROM dungeons")
    stats.dungeons = cursor.fetchone()[0]
    
    # Boss数量
    cursor.execute("SELECT COUNT(*) FROM bosses")
    stats.bosses = cursor.fetchone()[0]
    
    # 物品数量
    cursor.execute("SELECT COUNT(*) FROM items")
    items_count = cursor.fetchone()[0]
    # 如果没有items表，尝试loot_items
    if items_count == 0:
        try:
            cursor.execute("SELECT COUNT(*) FROM loot_items")
            items_count = cursor.fetchone()[0]
        except:
            pass
    stats.items = items_count
    
    conn.close()
    return stats


@router.delete("/clear-all")
async def clear_all_data():
    """清空所有数据（危险操作）"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 清空各表数据
        tables = ['characters', 'bosses', 'dungeons', 'items', 'loot_items', 
                  'character_items', 'gold_records', 'talents']
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
            except sqlite3.OperationalError:
                pass  # 表不存在则跳过
        
        conn.commit()
        conn.close()
        
        return {"message": "所有数据已清空"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"清空失败: {str(e)}")
