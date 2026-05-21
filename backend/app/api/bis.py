# -*- coding: utf-8 -*-
"""
BiS (Best in Slot) 毕业装备 API
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from app.core.database import db

router = APIRouter(prefix="/api/bis", tags=["bis"])

# BiS slot → character_equipment slot 映射
BIS_SLOT_TO_EQUIP = {
    'Head': ['HEAD'],
    'Neck': ['NECK'],
    'Shoulder': ['SHOULDER'],
    'Back': ['BACK'],
    'Chest': ['CHEST'],
    'Wrist': ['WRIST'],
    'Hands': ['HANDS'],
    'Waist': ['WAIST'],
    'Legs': ['LEGS'],
    'Feet': ['FEET'],
    'Finger': ['FINGER_1', 'FINGER_2'],
    'Trinket': ['TRINKET_1', 'TRINKET_2'],
    'Weapon': ['MAIN_HAND', '主手'],
    'Off hand': ['OFF_HAND', '副手'],
    'Ranged': ['RANGED', '远程'],
    'Relic': ['RANGED', '远程'],
    'Wrist': ['WRIST'],
}


class BiSImportRequest(BaseModel):
    class_name: str
    spec_name: str
    phase: str
    max_rank: int = 1  # 只导入排名1（最佳）


@router.get("/classes")
async def get_bis_classes():
    """获取所有有 BiS 数据的职业/天赋/阶段组合"""
    rows = await db.fetchall("""
        SELECT DISTINCT class_name, spec_name, phase
        FROM bis_lists
        ORDER BY class_name, spec_name, phase
    """)

    # 按职业分组
    classes = {}
    for r in rows:
        cls = r["class_name"]
        if cls not in classes:
            classes[cls] = {}
        spec = r["spec_name"]
        if spec not in classes[cls]:
            classes[cls][spec] = []
        if r["phase"] not in classes[cls][spec]:
            classes[cls][spec].append(r["phase"])

    return classes


@router.get("/")
async def get_bis_list(
    class_name: str,
    spec_name: str,
    phase: str,
    max_rank: int = 1,
):
    """查询指定职业/天赋/阶段的 BiS 列表"""
    rows = await db.fetchall("""
        SELECT b.*,
               bl.boss_id,
               bo.name AS boss_name,
               i.icon_url AS items_icon_url,
               i.quality AS items_quality,
               i.item_level AS items_item_level,
               i.stats AS items_stats
        FROM bis_lists b
        LEFT JOIN boss_loot bl ON b.item_id = bl.item_id
        LEFT JOIN bosses bo ON bl.boss_id = bo.id
        LEFT JOIN items i ON b.item_id = i.item_id
        WHERE b.class_name = ? AND b.spec_name = ? AND b.phase = ? AND b.rank <= ?
        ORDER BY b.slot, b.rank
    """, (class_name, spec_name, phase, max_rank))

    if not rows:
        raise HTTPException(status_code=404, detail="未找到 BiS 数据")

    # 去重 boss_id（一个物品可能被多个 boss 掉落）
    seen = set()
    result = []
    for r in rows:
        key = (r["class_name"], r["spec_name"], r["phase"], r["slot"], r["rank"], r["item_id"])
        if key not in seen:
            seen.add(key)
            result.append({
                "id": r["id"],
                "class_name": r["class_name"],
                "spec_name": r["spec_name"],
                "phase": r["phase"],
                "slot": r["slot"],
                "rank": r["rank"],
                "item_id": r["item_id"],
                "item_name": r["item_name"],
                "quality": (r["items_quality"] or r["quality"] or "").lower() or None,
                "item_level": r["items_item_level"] or r["item_level"],
                "icon_url": r["items_icon_url"] or r["icon_url"],
                "stats": r["items_stats"],
                "source": r["source"],
                "boss_name": r["boss_name"],
                "dungeon_name": r["dungeon_name"],
            })

    return result


@router.post("/import-needs/{character_id}")
async def import_bis_to_needs(character_id: int, request: BiSImportRequest):
    """将 BiS 列表导入到角色的装备需求(item_needs)"""
    # 验证角色存在
    char = await db.fetchone("SELECT id, name, wow_class FROM characters WHERE id = ?", (character_id,))
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 获取 BiS 数据
    rows = await db.fetchall("""
        SELECT * FROM bis_lists
        WHERE class_name = ? AND spec_name = ? AND phase = ? AND rank <= ?
        ORDER BY slot, rank
    """, (request.class_name, request.spec_name, request.phase, request.max_rank))

    if not rows:
        raise HTTPException(status_code=404, detail="未找到 BiS 数据")

    # 获取角色已有的 item_needs item_id 列表，避免重复导入
    existing = await db.fetchall(
        "SELECT item_id FROM item_needs WHERE character_id = ?",
        (character_id,)
    )
    existing_ids = {r["item_id"] for r in existing}

    # 每个 slot 只取 rank=1 的物品
    slot_added = set()
    added_count = 0
    skipped_count = 0

    for r in rows:
        slot = r["slot"]
        item_id = r["item_id"]

        # 每个 slot 只导入一个物品
        if slot in slot_added:
            continue

        # 跳过已存在的
        if item_id in existing_ids:
            skipped_count += 1
            slot_added.add(slot)
            continue

        await db.execute("""
            INSERT INTO item_needs (character_id, item_id, item_name, boss_name, dungeon_name, priority, obtained, notes)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            character_id,
            item_id,
            r["item_name"] or f"物品#{item_id}",
            r["source"],
            r["dungeon_name"],
            1,
            f"BiS {request.phase} {r['slot']}"
        ))

        added_count += 1
        slot_added.add(slot)

    return {
        "success": True,
        "message": f"导入完成: 新增 {added_count} 条, 跳过已有 {skipped_count} 条",
        "added": added_count,
        "skipped": skipped_count,
        "total_biS": len(rows)
    }


@router.get("/compare/{character_id}")
async def compare_character_bis(character_id: int):
    """对比角色当前装备与 BiS 毕业装，返回已获取和未获取的列表"""
    # 获取角色信息
    char = await db.fetchone(
        "SELECT id, name, wow_class, spec FROM characters WHERE id = ?",
        (character_id,)
    )
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 获取角色当前装备
    equip_rows = await db.fetchall(
        "SELECT item_id, name, slot, quality, item_level FROM character_equipment WHERE character_id = ?",
        (character_id,)
    )
    equipped_items = {}
    for eq in equip_rows:
        equipped_items[eq["item_id"]] = {
            "name": eq["name"],
            "slot": eq["slot"],
            "quality": eq["quality"],
            "item_level": eq["item_level"]
        }

    # 获取该职业的所有 BiS 数据（所有天赋、所有阶段）
    bis_rows = await db.fetchall("""
        SELECT b.*,
               i.icon_url AS items_icon_url,
               i.quality AS items_quality,
               i.item_level AS items_item_level,
               i.stats AS items_stats
        FROM bis_lists b
        LEFT JOIN items i ON b.item_id = i.item_id
        WHERE b.class_name = ? AND b.rank = 1
        ORDER BY b.slot, b.phase
    """, (char["wow_class"],))

    if not bis_rows:
        raise HTTPException(status_code=404, detail="未找到该职业的 BiS 数据")

    # 按 (spec, phase) 分组
    from collections import defaultdict
    spec_phase_groups = defaultdict(list)
    for r in bis_rows:
        spec_phase_groups[(r["spec_name"], r["phase"])].append(r)

    # 对每个 (spec, phase) 组合，对比装备
    comparisons = []
    for (spec_name, phase), items in spec_phase_groups.items():
        obtained = []
        missing = []
        for r in items:
            bis_item = {
                "item_id": r["item_id"],
                "item_name": r["item_name"],
                "slot": r["slot"],
                "quality": (r["items_quality"] or r["quality"] or "").lower() or None,
                "item_level": r["items_item_level"] or r["item_level"],
                "source": r["source"],
                "dungeon_name": r["dungeon_name"],
                "icon_url": r["items_icon_url"] or r["icon_url"],
                "stats": r["items_stats"],
            }
            # 检查角色是否已装备该物品
            if r["item_id"] in equipped_items:
                bis_item["equipped"] = equipped_items[r["item_id"]]
                obtained.append(bis_item)
            else:
                # 也检查同 slot 的其他装备（可能装备了不同物品）
                equip_slots = BIS_SLOT_TO_EQUIP.get(r["slot"], [])
                has_any = any(
                    eq_slot in [e["slot"] for e in equip_rows]
                    for eq_slot in equip_slots
                )
                bis_item["slot_occupied"] = has_any
                missing.append(bis_item)

        comparisons.append({
            "spec_name": spec_name,
            "phase": phase,
            "total": len(items),
            "obtained_count": len(obtained),
            "missing_count": len(missing),
            "obtained": obtained,
            "missing": missing
        })

    # 按 missing_count 升序排列（已获取最多的排前面）
    comparisons.sort(key=lambda x: (x["missing_count"], x["phase"]))

    return {
        "character_id": character_id,
        "character_name": char["name"],
        "wow_class": char["wow_class"],
        "comparisons": comparisons
    }
