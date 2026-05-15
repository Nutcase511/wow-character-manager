from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.schemas import DungeonResponse
from app.core.database import db
import json
import subprocess
import os
import sys

router = APIRouter()

# 导入脚本路径
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMPORT_SCRIPT = os.path.join(BACKEND_DIR, "import_from_atlasloot.py")


def _row_to_dungeon(row) -> dict:
    return {
        "id": row["id"],
        "dungeon_id": row["dungeon_id"],
        "name": row["name"],
        "description": row["description"],
        "map_name": row["map_name"],
        "minimum_level": row["minimum_level"],
        "modes": json.loads(row["modes"]) if row["modes"] else [],
        "expansion": row["expansion"] if "expansion" in row.keys() else "wotlk",
        "category": row["category"] if "category" in row.keys() else "dungeon",
        "phase": row["phase"] if "phase" in row.keys() else None,
        "icon_url": row["icon_url"],
        "created_at": row["created_at"],
    }


@router.get("/", response_model=List[DungeonResponse])
async def get_dungeons(expansion: Optional[str] = None, category: Optional[str] = None, phase: Optional[str] = None):
    """获取所有副本，支持按资料片、类型和阶段过滤"""
    query = "SELECT * FROM dungeons WHERE 1=1"
    params = []
    if expansion:
        query += " AND expansion = ?"
        params.append(expansion)
    if category:
        query += " AND category = ?"
        params.append(category)
    if phase:
        query += " AND phase = ?"
        params.append(phase)
    query += " ORDER BY dungeon_id"
    rows = await db.fetchall(query, params)
    return [DungeonResponse(**_row_to_dungeon(r)) for r in rows]


@router.get("/{dungeon_id}", response_model=DungeonResponse)
async def get_dungeon(dungeon_id: int):
    """获取指定副本"""
    row = await db.fetchone("SELECT * FROM dungeons WHERE id = ?", (dungeon_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Dungeon not found")
    return DungeonResponse(**_row_to_dungeon(row))


@router.post("/import-atlasloot")
async def import_from_atlasloot():
    """从AtlasLoot插件数据导入副本/Boss/掉落数据"""
    try:
        # 验证脚本存在
        if not os.path.exists(IMPORT_SCRIPT):
            raise HTTPException(status_code=500, detail=f"Import script not found: {IMPORT_SCRIPT}")
        
        # 调用导入脚本
        # Windows 下使用系统编码（GBK/CP936），避免乱码
        import locale
        enc = locale.getpreferredencoding(False) or 'utf-8'
        result = subprocess.run(
            [sys.executable, IMPORT_SCRIPT],
            capture_output=True,
            text=True,
            encoding=enc,
            timeout=120,
            cwd=os.path.dirname(IMPORT_SCRIPT)  # 设置工作目录
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail=f"Import failed: {result.stderr or result.stdout}"
            )
        
        # 解析输出获取统计信息
        output = result.stdout or ""
        stats = {
            "instances": 0,
            "bosses": 0,
            "items": 0,
            "loot": 0
        }
        
        # 从输出中提取统计数字
        import re
        m = re.search(r'副本:\s*(\d+)', output)
        if m:
            stats["instances"] = int(m.group(1))
        m = re.search(r'Boss:\s*(\d+)', output)
        if m:
            stats["bosses"] = int(m.group(1))
        m = re.search(r'物品:\s*(\d+)', output)
        if m:
            stats["items"] = int(m.group(1))
        m = re.search(r'掉落关联:\s*(\d+)', output)
        if m:
            stats["loot"] = int(m.group(1))
        
        return {
            "success": True,
            "message": "数据导入成功",
            "stats": stats,
            "output": output
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Import timeout (120s)")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")
