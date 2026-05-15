from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.schemas.schemas import BossResponse
from app.core.database import db

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
                  i.quality, i.item_level, i.slot, i.icon_url, i.stats
           FROM boss_loot bl
           LEFT JOIN items i ON bl.item_id = i.item_id
           WHERE bl.boss_id = ?
           ORDER BY bl.id""",
        (boss_id,)
    )
    result = []
    for row in rows:
        row_dict = dict(row)
        if row_dict.get('stats'):
            try:
                import json
                row_dict['stats'] = json.loads(row_dict['stats'])
            except:
                row_dict['stats'] = {}
        else:
            row_dict['stats'] = {}
        result.append(row_dict)
    return result


@router.get("/item/{item_id}")
async def get_item_detail(item_id: int):
    """获取装备详情"""
    row = await db.fetchone(
        "SELECT * FROM items WHERE item_id = ?",
        (item_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    result = dict(row)
    if result.get('stats'):
        try:
            import json
            result['stats'] = json.loads(result['stats'])
        except:
            result['stats'] = {}
    else:
        result['stats'] = {}

    return result
