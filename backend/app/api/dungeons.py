from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.schemas import DungeonCreate, DungeonResponse
from app.core.database import db
import json
from datetime import datetime

router = APIRouter()


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
        "icon_url": row["icon_url"],
        "created_at": row["created_at"],
    }


@router.post("/", response_model=DungeonResponse)
async def create_dungeon(dungeon: DungeonCreate):
    """创建副本"""
    now = datetime.utcnow().isoformat()
    cursor = await db.execute(
        """INSERT INTO dungeons (dungeon_id, name, description, map_name, minimum_level, modes, expansion, category, icon_url, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (dungeon.dungeon_id, dungeon.name, dungeon.description, dungeon.map_name,
         dungeon.minimum_level, json.dumps(dungeon.modes), dungeon.expansion, dungeon.category, dungeon.icon_url, now)
    )
    row = await db.fetchone("SELECT * FROM dungeons WHERE id = ?", (cursor.lastrowid,))
    return DungeonResponse(**_row_to_dungeon(row))


@router.get("/", response_model=List[DungeonResponse])
async def get_dungeons(expansion: Optional[str] = None, category: Optional[str] = None):
    """获取所有副本，支持按资料片和类型过滤"""
    query = "SELECT * FROM dungeons WHERE 1=1"
    params = []
    if expansion:
        query += " AND expansion = ?"
        params.append(expansion)
    if category:
        query += " AND category = ?"
        params.append(category)
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


@router.post("/sync/{journal_instance_id}")
async def sync_dungeon_from_blizzard(journal_instance_id: int):
    """手动同步副本数据（本地模式）"""
    row = await db.fetchone("SELECT * FROM dungeons WHERE dungeon_id = ?", (journal_instance_id,))
    if row:
        return DungeonResponse(**_row_to_dungeon(row))
    raise HTTPException(status_code=404, detail="Dungeon not found. Use POST / to create manually.")


@router.delete("/{dungeon_id}")
async def delete_dungeon(dungeon_id: int):
    """删除副本"""
    cursor = await db.execute("DELETE FROM dungeons WHERE id = ?", (dungeon_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dungeon not found")
    return {"message": "Dungeon deleted successfully"}
