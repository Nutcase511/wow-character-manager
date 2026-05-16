from fastapi import APIRouter, HTTPException
from typing import Optional
from app.core.database import db

router = APIRouter()


@router.post("/fetch-icons")
async def fetch_missing_icons():
    """通过交叉引用 character_equipment 表，补全 items 表和 bis_lists 表中缺失的 icon_url"""
    # 找到 items 表中 icon_url 缺失的记录
    missing_items = await db.fetchall(
        "SELECT item_id, name FROM items WHERE icon_url IS NULL OR icon_url = ''"
    )

    if not missing_items:
        return {"updated": 0, "message": "所有物品已有图标"}

    missing_ids = [r["item_id"] for r in missing_items]

    # 从 character_equipment 中查找这些 item_id 对应的 icon_url
    placeholders = ','.join(['?' for _ in missing_ids])
    found_icons = await db.fetchall(
        f"SELECT DISTINCT item_id, icon_url FROM character_equipment WHERE item_id IN ({placeholders}) AND icon_url IS NOT NULL AND icon_url != ''",
        tuple(missing_ids)
    )

    # 也检查 bis_lists 表中已有的 icon_url
    bis_icons = await db.fetchall(
        f"SELECT DISTINCT item_id, icon_url FROM bis_lists WHERE item_id IN ({placeholders}) AND icon_url IS NOT NULL AND icon_url != ''",
        tuple(missing_ids)
    )

    # 合并
    icon_map = {}
    for r in found_icons:
        icon_map[r["item_id"]] = r["icon_url"]
    for r in bis_icons:
        if r["item_id"] not in icon_map:
            icon_map[r["item_id"]] = r["icon_url"]

    if not icon_map:
        return {"updated": 0, "message": "在 character_equipment 和 bis_lists 表中未找到图标数据", "missing": missing_ids}

    # 更新 items 表
    updated = 0
    for item_id, icon_url in icon_map.items():
        await db.execute(
            "UPDATE items SET icon_url = ? WHERE item_id = ? AND (icon_url IS NULL OR icon_url = '')",
            (icon_url, item_id)
        )
        updated += 1

    # 也同步更新 bis_lists 表
    bis_updated = 0
    for item_id, icon_url in icon_map.items():
        await db.execute(
            "UPDATE bis_lists SET icon_url = ? WHERE item_id = ? AND (icon_url IS NULL OR icon_url = '')",
            (icon_url, item_id)
        )
        bis_updated += 1

    return {
        "updated": updated,
        "bis_updated": bis_updated,
        "message": f"更新了 {updated} 个物品和 {bis_updated} 条 BiS 数据的图标"
    }


@router.get("/{item_id}")
async def get_item(item_id: int):
    """获取物品信息"""
    row = await db.fetchone(
        "SELECT * FROM items WHERE item_id = ?",
        (item_id,)
    )
    if not row:
        # 如果数据库中没有，返回基本结构
        return {
            "item_id": item_id,
            "name": f"物品 #{item_id}",
            "quality": "common",
            "item_level": 0,
            "icon_url": None,
            "slot": None,
            "stats": []
        }
    
    return {
        "item_id": row["item_id"],
        "name": row["name"],
        "quality": row["quality"],
        "item_level": row["item_level"],
        "icon_url": row["icon_url"],
        "slot": row["slot"],
        "stats": row["stats"]
    }


@router.post("/batch")
async def get_items_batch(item_ids: list[int]):
    """批量获取物品信息"""
    if not item_ids:
        return {}
    
    # 构建占位符
    placeholders = ','.join(['?' for _ in item_ids])
    rows = await db.fetchall(
        f"SELECT * FROM items WHERE item_id IN ({placeholders})",
        tuple(item_ids)
    )
    
    # 构建结果字典
    result = {}
    for row in rows:
        result[row["item_id"]] = {
            "item_id": row["item_id"],
            "name": row["name"],
            "quality": row["quality"],
            "item_level": row["item_level"],
            "icon_url": row["icon_url"],
            "slot": row["slot"],
            "stats": row["stats"]
        }
    
    # 为未找到的物品添加默认值
    for item_id in item_ids:
        if item_id not in result:
            result[item_id] = {
                "item_id": item_id,
                "name": f"物品 #{item_id}",
                "quality": "common",
                "item_level": 0,
                "icon_url": None,
                "slot": None,
                "stats": []
            }
    
    return result
