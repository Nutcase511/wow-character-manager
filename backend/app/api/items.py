from fastapi import APIRouter, HTTPException
from typing import Optional
from app.core.database import db

router = APIRouter()

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
