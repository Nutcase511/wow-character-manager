from fastapi import APIRouter, HTTPException
from typing import List, Optional
import json
from datetime import datetime
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

# tdInspect 装备槽位顺序（按 Lua 表索引）
TDINSPECT_SLOT_ORDER = [
    "头部", "颈部", "肩部", "衬衣", "胸部", "腰部",
    "腿部", "脚部", "手腕", "手套",
    "手指1", "手指2", "饰品1", "饰品2",
    "背部", "主手", "副手", "远程", "战袍"
]

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
    """同步角色装备数据（从前端传入的暴雪 API 数据），持久化到 character_equipment 和 character_item_sets 表"""
    # 验证角色存在
    row = await db.fetchone(
        "SELECT id FROM characters WHERE id = ?",
        (character_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="角色不存在")

    equipped_items = equipment_data.get("equipped_items", [])

    # 处理并持久化装备数据
    items = []
    for item_data in equipped_items:
        item_info = item_data.get("item", {})
        item_id = item_info.get("id", 0)
        item_name = item_data.get("name", "")
        slot_type = item_data.get("slot", {}).get("type", "")
        slot_name = EQUIPMENT_SLOTS.get(slot_type, slot_type)
        quality = item_data.get("quality", {}).get("type", "")
        quality_value = item_data.get("quality", {}).get("value", 0)

        # 物品等级
        item_level = 0
        if "requirements" in item_data and "level" in item_data["requirements"]:
            item_level = item_data["requirements"]["level"].get("value", 0)

        # 护甲值
        armor = item_data.get("armor", {}).get("value", 0)

        # 耐久度
        durability_current = item_data.get("durability", {}).get("value", 0)
        durability_max = 0
        if "durability" in item_data and "display_string" in item_data["durability"]:
            dur_str = item_data["durability"]["display_string"]
            if "/" in dur_str:
                try:
                    durability_max = int(dur_str.split("/")[-1].strip())
                except ValueError:
                    pass

        # 卖价
        sell_price = item_data.get("sell_price", {}).get("value", 0)

        # 绑定类型
        binding = item_data.get("binding", {}).get("type", "")

        # 图标
        icon_url = item_data.get("media", {}).get("icon", "")

        # 属性
        stats_json = []
        for stat in item_data.get("stats", []):
            stats_json.append({
                "type": stat["type"]["type"],
                "name": stat["type"]["name"],
                "value": stat["value"],
                "display": stat["display"]["display_string"],
                "is_equip_bonus": stat.get("is_equip_bonus", False)
            })

        # 附魔
        enchantments_json = []
        for enchant in item_data.get("enchantments", []):
            enchantments_json.append({
                "display_string": enchant["display_string"],
                "enchantment_id": enchant.get("enchantment_id", 0),
                "source_item": enchant.get("source_item", {})
            })

        # 宝石插槽
        sockets_json = []
        for enchant in item_data.get("enchantments", []):
            slot_id = enchant.get("enchantment_slot", {}).get("id", 0)
            if slot_id >= 2:
                sockets_json.append({
                    "gem": enchant.get("source_item", {}),
                    "display_string": enchant["display_string"]
                })

        # 特效
        spells_json = []
        for spell in item_data.get("spells", []):
            spells_json.append({
                "name": spell["spell"]["name"],
                "description": spell["description"],
                "spell_id": spell["spell"]["id"]
            })

        # 套装信息
        item_set_id = 0
        item_set_name = ""
        if "set" in item_data and item_data["set"].get("item_set"):
            item_set_id = item_data["set"]["item_set"].get("id", 0)
            item_set_name = item_data["set"]["item_set"].get("name", "")

        # 写入 character_equipment 表
        await db.execute("""
            INSERT INTO character_equipment
            (character_id, item_id, name, slot, quality, item_level, icon_url, armor,
             stats, enchantments, sockets, spells, binding, durability_current, durability_max,
             sell_price, item_set_id, item_set_name, is_equipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(character_id, slot) DO UPDATE SET
            item_id = excluded.item_id,
            name = excluded.name,
            quality = excluded.quality,
            item_level = excluded.item_level,
            icon_url = excluded.icon_url,
            armor = excluded.armor,
            stats = excluded.stats,
            enchantments = excluded.enchantments,
            sockets = excluded.sockets,
            spells = excluded.spells,
            binding = excluded.binding,
            durability_current = excluded.durability_current,
            durability_max = excluded.durability_max,
            sell_price = excluded.sell_price,
            item_set_id = excluded.item_set_id,
            item_set_name = excluded.item_set_name,
            is_equipped = excluded.is_equipped,
            updated_at = CURRENT_TIMESTAMP
        """, (
            character_id, item_id, item_name, slot_name, quality, item_level, icon_url, armor,
            json.dumps(stats_json, ensure_ascii=False),
            json.dumps(enchantments_json, ensure_ascii=False),
            json.dumps(sockets_json, ensure_ascii=False),
            json.dumps(spells_json, ensure_ascii=False),
            binding, durability_current, durability_max, sell_price,
            item_set_id, item_set_name, 1
        ))

        items.append({
            "slot": slot_name,
            "slot_type": slot_type,
            "item_id": item_id,
            "name": item_name,
            "quality": quality,
            "quality_value": quality_value,
            "item_level": item_level,
            "icon": item_data.get("media", {}).get("key", {}).get("href", ""),
        })

    # 处理套装数据
    equipped_sets = equipment_data.get("equipped_item_sets", [])
    for set_data in equipped_sets:
        item_set = set_data.get("item_set", {})
        if not item_set.get("id"):
            continue

        set_id = item_set["id"]
        set_name = item_set["name"]

        equipped_count = 0
        total_count = 0
        items_json = []
        for s_item in set_data.get("items", []):
            total_count += 1
            if s_item.get("is_equipped"):
                equipped_count += 1
            items_json.append({
                "id": s_item["item"]["id"],
                "name": s_item["item"]["name"],
                "is_equipped": s_item.get("is_equipped", False)
            })

        effects_json = []
        for effect in set_data.get("effects", []):
            effects_json.append({
                "display_string": effect["display_string"],
                "required_count": effect.get("required_count", 0),
                "is_active": effect.get("is_active", False)
            })

        await db.execute("""
            INSERT INTO character_item_sets
            (character_id, set_id, set_name, equipped_count, total_count, effects, items)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(character_id, set_id) DO UPDATE SET
            set_name = excluded.set_name,
            equipped_count = excluded.equipped_count,
            total_count = excluded.total_count,
            effects = excluded.effects,
            items = excluded.items,
            updated_at = CURRENT_TIMESTAMP
        """, (
            character_id, set_id, set_name, equipped_count, total_count,
            json.dumps(effects_json, ensure_ascii=False),
            json.dumps(items_json, ensure_ascii=False)
        ))

    # 同时更新 characters 表的 equips_data 和 last_sync_at
    await db.execute(
        "UPDATE characters SET equips_data = ?, last_sync_at = ? WHERE id = ?",
        (json.dumps(items, ensure_ascii=False), datetime.utcnow().isoformat(), character_id)
    )

    # 计算平均装等
    valid_items = [i for i in items if i["item_level"] > 0]
    avg_ilvl = round(sum(i["item_level"] for i in valid_items) / len(valid_items)) if valid_items else 0

    return {
        "character_id": character_id,
        "equipped_items": items,
        "average_item_level": equipment_data.get("average_item_level", avg_ilvl),
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


@router.get("/{character_id}/item-sets")
async def get_character_item_sets(character_id: int):
    """获取角色的套装收集进度"""
    # 验证角色存在
    row = await db.fetchone(
        "SELECT name FROM characters WHERE id = ?",
        (character_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="角色不存在")

    sets_rows = await db.fetchall(
        "SELECT * FROM character_item_sets WHERE character_id = ? ORDER BY set_name",
        (character_id,)
    )

    item_sets = []
    for s in sets_rows:
        effects = json.loads(s["effects"]) if s["effects"] else []
        items = json.loads(s["items"]) if s["items"] else []

        item_sets.append({
            "id": s["id"],
            "set_id": s["set_id"],
            "set_name": s["set_name"],
            "equipped_count": s["equipped_count"],
            "total_count": s["total_count"],
            "effects": effects,
            "items": items,
            "updated_at": s["updated_at"]
        })

    # 也从 character_equipment 中提取套装信息（补充从 tdInspect 导入的套装）
    equip_sets = await db.fetchall("""
        SELECT item_set_id, item_set_name, COUNT(*) as equipped_count
        FROM character_equipment
        WHERE character_id = ? AND item_set_id > 0 AND item_set_name != ''
        GROUP BY item_set_id, item_set_name
    """, (character_id,))

    # 合并：如果 character_item_sets 中没有但 equipment 中有
    existing_set_ids = {s["set_id"] for s in item_sets}
    for es in equip_sets:
        if es["item_set_id"] not in existing_set_ids:
            item_sets.append({
                "id": 0,
                "set_id": es["item_set_id"],
                "set_name": es["item_set_name"],
                "equipped_count": es["equipped_count"],
                "total_count": 0,
                "effects": [],
                "items": [],
                "updated_at": None
            })
            existing_set_ids.add(es["item_set_id"])

    return {
        "character_id": character_id,
        "character_name": row["name"],
        "item_sets": item_sets,
        "count": len(item_sets)
    }
