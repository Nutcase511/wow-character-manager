from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
from app.schemas.schemas import ItemNeedCreate, ItemNeedResponse
from app.core.database import db
from datetime import datetime

router = APIRouter()


def _row_to_item_need(row) -> dict:
    stats = row["items_stats"]
    if stats:
        try:
            stats = json.loads(stats) if isinstance(stats, str) else stats
        except (json.JSONDecodeError, TypeError):
            stats = {}
    else:
        stats = {}
    return {
        "id": row["id"],
        "character_id": str(row["character_id"]),
        "item_id": row["item_id"],
        "item_name": row["items_item_name"] or row["item_name"] or f"物品#{row['item_id']}",
        "boss_id": row["boss_id"],
        "boss_name": row["boss_name"],
        "dungeon_name": row["dungeon_name"],
        "priority": row["priority"],
        "obtained": bool(row["obtained"]),
        "notes": row["notes"],
        "icon_url": row["items_icon_url"],
        "stats": stats,
        "quality": row["items_quality"],
        "item_level": row["items_item_level"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.post("/", response_model=ItemNeedResponse)
async def create_item_need(item_need: ItemNeedCreate):
    """创建装备需求"""
    char_row = await db.fetchone("SELECT id FROM characters WHERE id = ?", (int(item_need.character_id),))
    if not char_row:
        raise HTTPException(status_code=404, detail="Character not found")

    now = datetime.utcnow().isoformat()
    cursor = await db.execute(
        """INSERT INTO item_needs (character_id, item_id, item_name, boss_id, boss_name,
           dungeon_name, priority, obtained, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (int(item_need.character_id), item_need.item_id, item_need.item_name,
         item_need.boss_id, item_need.boss_name, item_need.dungeon_name,
         item_need.priority, 1 if item_need.obtained else 0, item_need.notes, now, now)
    )
    row = await db.fetchone("""
        SELECT n.*,
               i.name AS items_item_name,
               i.icon_url AS items_icon_url,
               i.stats AS items_stats,
               i.quality AS items_quality,
               i.item_level AS items_item_level
        FROM item_needs n
        LEFT JOIN items i ON n.item_id = i.item_id
        WHERE n.id = ?
    """, (cursor.lastrowid,))
    return ItemNeedResponse(**_row_to_item_need(row))


@router.get("/", response_model=List[ItemNeedResponse])
async def get_item_needs(character_id: Optional[str] = None, obtained: Optional[bool] = None):
    """获取装备需求列表"""
    query = """
        SELECT n.*,
               i.name AS items_item_name,
               i.icon_url AS items_icon_url,
               i.stats AS items_stats,
               i.quality AS items_quality,
               i.item_level AS items_item_level
        FROM item_needs n
        LEFT JOIN items i ON n.item_id = i.item_id
        WHERE 1=1
    """
    params = []

    if character_id is not None:
        query += " AND n.character_id = ?"
        params.append(int(character_id))
    if obtained is not None:
        query += " AND n.obtained = ?"
        params.append(1 if obtained else 0)

    query += " ORDER BY n.id DESC"
    rows = await db.fetchall(query, params)
    return [ItemNeedResponse(**_row_to_item_need(r)) for r in rows]


@router.get("/{need_id}", response_model=ItemNeedResponse)
async def get_item_need(need_id: int):
    """获取指定装备需求"""
    row = await db.fetchone("""
        SELECT n.*,
               i.name AS items_item_name,
               i.icon_url AS items_icon_url,
               i.stats AS items_stats,
               i.quality AS items_quality,
               i.item_level AS items_item_level
        FROM item_needs n
        LEFT JOIN items i ON n.item_id = i.item_id
        WHERE n.id = ?
    """, (need_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Item need not found")
    return ItemNeedResponse(**_row_to_item_need(row))


@router.put("/{need_id}", response_model=ItemNeedResponse)
async def update_item_need(need_id: int, item_need: ItemNeedCreate):
    """更新装备需求"""
    now = datetime.utcnow().isoformat()
    cursor = await db.execute(
        """UPDATE item_needs SET character_id=?, item_id=?, item_name=?, boss_id=?, boss_name=?,
           dungeon_name=?, priority=?, obtained=?, notes=?, updated_at=?
           WHERE id=?""",
        (int(item_need.character_id), item_need.item_id, item_need.item_name,
         item_need.boss_id, item_need.boss_name, item_need.dungeon_name,
         item_need.priority, 1 if item_need.obtained else 0, item_need.notes, now, need_id)
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item need not found")
    row = await db.fetchone("""
        SELECT n.*,
               i.name AS items_item_name,
               i.icon_url AS items_icon_url,
               i.stats AS items_stats,
               i.quality AS items_quality,
               i.item_level AS items_item_level
        FROM item_needs n
        LEFT JOIN items i ON n.item_id = i.item_id
        WHERE n.id = ?
    """, (need_id,))
    return ItemNeedResponse(**_row_to_item_need(row))


@router.patch("/{need_id}/obtain", response_model=ItemNeedResponse)
async def mark_item_obtained(need_id: int):
    """标记装备已获得"""
    now = datetime.utcnow().isoformat()
    cursor = await db.execute("UPDATE item_needs SET obtained = 1, updated_at = ? WHERE id = ?", (now, need_id))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item need not found")
    row = await db.fetchone("""
        SELECT n.*,
               i.name AS items_item_name,
               i.icon_url AS items_icon_url,
               i.stats AS items_stats,
               i.quality AS items_quality,
               i.item_level AS items_item_level
        FROM item_needs n
        LEFT JOIN items i ON n.item_id = i.item_id
        WHERE n.id = ?
    """, (need_id,))
    return ItemNeedResponse(**_row_to_item_need(row))


@router.delete("/{need_id}")
async def delete_item_need(need_id: int):
    """删除装备需求"""
    cursor = await db.execute("DELETE FROM item_needs WHERE id = ?", (need_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item need not found")
    return {"message": "Item need deleted successfully"}


@router.get("/character/{character_id}/progress")
async def get_character_item_progress(character_id: str):
    """获取角色装备进度"""
    char_row = await db.fetchone("SELECT name FROM characters WHERE id = ?", (int(character_id),))
    if not char_row:
        raise HTTPException(status_code=404, detail="Character not found")

    row = await db.fetchone(
        "SELECT COUNT(*) as total, SUM(CASE WHEN obtained = 1 THEN 1 ELSE 0 END) as obtained FROM item_needs WHERE character_id = ?",
        (int(character_id),)
    )
    total = row["total"]
    obtained = row["obtained"] or 0

    return {
        "character_id": character_id,
        "character_name": char_row["name"],
        "total_needs": total,
        "obtained": obtained,
        "remaining": total - obtained,
        "progress_percentage": round((obtained / total * 100) if total > 0 else 0, 1)
    }
