from fastapi import APIRouter, HTTPException
from typing import List, Optional
import httpx
from app.core.database import db

router = APIRouter(prefix="/api/characters", tags=["equipment"])

# 装备槽位映射（根据暴雪 API 的 slot 字段）
EQUIPMENT_SLOTS = {
    "HEAD": "头部",
    "NECK": "颈部",
    "SHOULDER": "肩部",
    "BACK": "背部",
    "CHEST": "胸部",
    "SHIRT": "衬衣",
    "TABARD": "战袍",
    "WRIST": "手腕",
    "HANDS": "手套",
    "WAIST": "腰部",
    "LEGS": "腿部",
    "FEET": "脚部",
    "FINGER_1": "手指1",
    "FINGER_2": "手指2",
    "TRINKET_1": "饰品1",
    "TRINKET_2": "饰品2",
    "MAIN_HAND": "主手",
    "OFF_HAND": "副手",
    "RANGED": "远程",
}

# 品质颜色映射
QUALITY_COLORS = {
    0: "#9d9d9d",  # 粗糙
    1: "#ffffff",  # 普通
    2: "#1eff00",  # 优秀
    3: "#0070dd",  # 精良
    4: "#a335ee",  # 史诗
    5: "#ff8000",  # 传说
}


@router.get("/{character_id}/equipment")
async def get_character_equipment(character_id: int):
    """获取角色装备信息（从数据库）"""
    # 获取角色信息
    row = await db.fetchone(
        "SELECT name, realm FROM characters WHERE id = ?",
        (character_id,)
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 从数据库获取装备
    equipment_rows = await db.fetchall(
        "SELECT * FROM character_equipment WHERE character_id = ? ORDER BY slot",
        (character_id,)
    )
    
    equipped_items = []
    for item in equipment_rows:
        equipped_items.append({
            "id": item["id"],
            "item_id": item["item_id"],
            "name": item["name"],
            "slot": item["slot"],
            "slot_type": item["slot"],
            "quality": item["quality"],
            "quality_value": item["quality"],
            "item_level": item["item_level"],
            "icon_url": item["icon_url"],
            "armor": item["armor"],
            "stats": item["stats"],
            "enchantments": item["enchantments"],
            "sockets": item["sockets"],
            "spells": item["spells"],
            "binding": item["binding"],
            "durability_current": item["durability_current"],
            "durability_max": item["durability_max"],
            "sell_price": item["sell_price"],
            "item_set_id": item["item_set_id"],
            "item_set_name": item["item_set_name"],
            "equipped_at": item["equipped_at"],
            "updated_at": item["updated_at"]
        })
    
    # 计算平均装等
    valid_items = [i for i in equipped_items if i["item_level"] > 0]
    avg_item_level = round(sum(i["item_level"] for i in valid_items) / len(valid_items)) if valid_items else 0
    
    return {
        "character_id": character_id,
        "character_name": row["name"],
        "realm": row["realm"],
        "equipped_items": equipped_items,
        "average_item_level": avg_item_level,
        "count": len(equipped_items)
    }


@router.post("/{character_id}/equipment/sync")
async def sync_character_equipment(character_id: int, equipment_data: dict):
    """同步角色装备数据（从前端传入的暴雪 API 数据）"""
    # 验证角色存在
    row = await db.fetchone(
        "SELECT id FROM characters WHERE id = ?",
        (character_id,)
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    equipped_items = equipment_data.get("equipped_items", [])
    
    # 处理装备数据
    items = []
    for item in equipped_items:
        slot_type = item.get("slot", {}).get("type", "")
        slot_name = EQUIPMENT_SLOTS.get(slot_type, slot_type)
        
        processed_item = {
            "slot": slot_name,
            "slot_type": slot_type,
            "item_id": item.get("item_id"),
            "name": item.get("name"),
            "quality": item.get("quality", {}).get("type"),
            "quality_value": item.get("quality", {}).get("value", 0),
            "item_level": item.get("level", {}).get("value", 0),
            "icon": item.get("media", {}).get("key", {}).get("href", ""),
        }
        items.append(processed_item)
    
    # 保存到数据库（可选）
    # 这里可以创建一个 equipment 表来存储装备历史
    
    return {
        "character_id": character_id,
        "equipped_items": items,
        "average_item_level": equipment_data.get("average_item_level", 0),
        "count": len(items)
    }


@router.get("/{character_id}/equipment/slots")
async def get_equipment_slots():
    """获取装备槽位定义"""
    return {
        "slots": [
            {"type": "HEAD", "name": "头部"},
            {"type": "NECK", "name": "颈部"},
            {"type": "SHOULDER", "name": "肩部"},
            {"type": "BACK", "name": "背部"},
            {"type": "CHEST", "name": "胸部"},
            {"type": "WRIST", "name": "手腕"},
            {"type": "HANDS", "name": "手套"},
            {"type": "WAIST", "name": "腰部"},
            {"type": "LEGS", "name": "腿部"},
            {"type": "FEET", "name": "脚部"},
            {"type": "FINGER_1", "name": "手指1"},
            {"type": "FINGER_2", "name": "手指2"},
            {"type": "TRINKET_1", "name": "饰品1"},
            {"type": "TRINKET_2", "name": "饰品2"},
            {"type": "MAIN_HAND", "name": "主手"},
            {"type": "OFF_HAND", "name": "副手"},
            {"type": "RANGED", "name": "远程"},
        ]
    }
