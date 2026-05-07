from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.schemas import BossCreate, BossResponse
from app.core.database import db
from datetime import datetime

router = APIRouter()


def _row_to_boss(row) -> dict:
    return {
        "id": row["id"],
        "boss_id": row["boss_id"],
        "name": row["name"],
        "description": row["description"],
        "dungeon_id": row["dungeon_id"],
        "dungeon_name": row["dungeon_name"],
        "category": row["category"],
        "icon_url": row["icon_url"],
        "created_at": row["created_at"],
    }


@router.post("/", response_model=BossResponse)
async def create_boss(boss: BossCreate):
    """创建Boss"""
    now = datetime.utcnow().isoformat()
    cursor = await db.execute(
        """INSERT INTO bosses (boss_id, name, description, dungeon_id, dungeon_name, category, icon_url, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (boss.boss_id, boss.name, boss.description, boss.dungeon_id,
         boss.dungeon_name, boss.category, boss.icon_url, now)
    )
    row = await db.fetchone("SELECT * FROM bosses WHERE id = ?", (cursor.lastrowid,))
    return BossResponse(**_row_to_boss(row))


@router.get("/", response_model=List[BossResponse])
async def get_bosses(dungeon_id: Optional[int] = None):
    """获取所有Boss"""
    if dungeon_id:
        rows = await db.fetchall("SELECT * FROM bosses WHERE dungeon_id = ? ORDER BY id", (dungeon_id,))
    else:
        rows = await db.fetchall("SELECT * FROM bosses ORDER BY id")
    return [BossResponse(**_row_to_boss(r)) for r in rows]


@router.get("/dungeon/{dungeon_id}/bosses", response_model=List[BossResponse])
async def get_bosses_by_dungeon(dungeon_id: int):
    """获取指定副本的所有Boss"""
    rows = await db.fetchall("SELECT * FROM bosses WHERE dungeon_id = ? ORDER BY id", (dungeon_id,))
    return [BossResponse(**_row_to_boss(r)) for r in rows]


@router.get("/lookup/{boss_id}", response_model=BossResponse)
async def lookup_boss_by_boss_id(boss_id: int):
    """通过boss_id查找Boss"""
    row = await db.fetchone("SELECT * FROM bosses WHERE boss_id = ?", (boss_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Boss not found")
    return BossResponse(**_row_to_boss(row))


@router.get("/{boss_id}", response_model=BossResponse)
async def get_boss(boss_id: int):
    """获取指定Boss"""
    row = await db.fetchone("SELECT * FROM bosses WHERE id = ?", (boss_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Boss not found")
    return BossResponse(**_row_to_boss(row))


@router.get("/{boss_id}/loot")
async def get_boss_loot(boss_id: int):
    """获取指定Boss的掉落装备列表"""
    rows = await db.fetchall(
        """SELECT bl.item_id, bl.item_name, bl.difficulty,
                  i.quality, i.item_level, i.slot, i.icon_url
           FROM boss_loot bl
           LEFT JOIN items i ON bl.item_id = i.item_id
           WHERE bl.boss_id = ?
           ORDER BY bl.id""",
        (boss_id,)
    )
    return [dict(r) for r in rows]


@router.post("/sync/{journal_encounter_id}")
async def sync_boss_from_blizzard(journal_encounter_id: int):
    """手动同步Boss数据（本地模式）"""
    row = await db.fetchone("SELECT * FROM bosses WHERE boss_id = ?", (journal_encounter_id,))
    if row:
        return BossResponse(**_row_to_boss(row))
    raise HTTPException(status_code=404, detail="Boss not found. Use POST / to create manually.")


@router.delete("/{boss_id}")
async def delete_boss(boss_id: int):
    """删除Boss"""
    cursor = await db.execute("DELETE FROM bosses WHERE id = ?", (boss_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Boss not found")
    return {"message": "Boss deleted successfully"}
