from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.schemas import ItemNeedCreate, ItemNeedResponse
from app.core.database import db
from app.services.blizzard_api import blizzard_api
from datetime import datetime
from bson import ObjectId

router = APIRouter()


@router.post("/", response_model=ItemNeedResponse)
async def create_item_need(item_need: ItemNeedCreate):
    """创建装备需求"""
    # 验证角色是否存在
    character = await db.get_database()["characters"].find_one({"_id": ObjectId(item_need.character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # 从暴雪API获取装备信息
    item_details = await blizzard_api.get_item_details(item_need.item_id)
    if item_details:
        # 更新或创建装备记录
        existing_item = await db.get_database()["items"].find_one({"item_id": item_need.item_id})
        if not existing_item:
            item_data = {
                "item_id": item_details["id"],
                "name": item_details["name"],
                "quality": item_details["quality"],
                "item_level": item_details["level"],
                "slot": item_details.get("inventory_type"),
                "stats": item_details.get("stats", {}),
                "icon_url": item_details.get("icon"),
                "created_at": datetime.utcnow()
            }
            await db.get_database()["items"].insert_one(item_data)

    item_need_data = item_need.dict()
    item_need_data["created_at"] = datetime.utcnow()
    item_need_data["updated_at"] = datetime.utcnow()

    result = await db.get_database()["item_needs"].insert_one(item_need_data)
    created_item_need = await db.get_database()["item_needs"].find_one({"_id": result.inserted_id})

    return ItemNeedResponse(**created_item_need)


@router.get("/", response_model=List[ItemNeedResponse])
async def get_item_needs(character_id: str = None, obtained: bool = None):
    """获取装备需求列表"""
    query = {}
    if character_id:
        query["character_id"] = character_id
    if obtained is not None:
        query["obtained"] = obtained

    item_needs = await db.get_database()["item_needs"].find(query).to_list(length=100)
    return [ItemNeedResponse(**item) for item in item_needs]


@router.get("/{need_id}", response_model=ItemNeedResponse)
async def get_item_need(need_id: str):
    """获取指定装备需求"""
    if not ObjectId.is_valid(need_id):
        raise HTTPException(status_code=400, detail="Invalid item need ID")

    item_need = await db.get_database()["item_needs"].find_one({"_id": ObjectId(need_id)})
    if not item_need:
        raise HTTPException(status_code=404, detail="Item need not found")

    return ItemNeedResponse(**item_need)


@router.put("/{need_id}", response_model=ItemNeedResponse)
async def update_item_need(need_id: str, item_need: ItemNeedCreate):
    """更新装备需求"""
    if not ObjectId.is_valid(need_id):
        raise HTTPException(status_code=400, detail="Invalid item need ID")

    item_need_data = item_need.dict()
    item_need_data["updated_at"] = datetime.utcnow()

    result = await db.get_database()["item_needs"].update_one(
        {"_id": ObjectId(need_id)},
        {"$set": item_need_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item need not found")

    updated_item_need = await db.get_database()["item_needs"].find_one({"_id": ObjectId(need_id)})
    return ItemNeedResponse(**updated_item_need)


@router.patch("/{need_id}/obtain")
async def mark_item_obtained(need_id: str):
    """标记装备已获取"""
    if not ObjectId.is_valid(need_id):
        raise HTTPException(status_code=400, detail="Invalid item need ID")

    result = await db.get_database()["item_needs"].update_one(
        {"_id": ObjectId(need_id)},
        {"$set": {"obtained": True, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item need not found")

    updated_item_need = await db.get_database()["item_needs"].find_one({"_id": ObjectId(need_id)})
    return ItemNeedResponse(**updated_item_need)


@router.delete("/{need_id}")
async def delete_item_need(need_id: str):
    """删除装备需求"""
    if not ObjectId.is_valid(need_id):
        raise HTTPException(status_code=400, detail="Invalid item need ID")

    result = await db.get_database()["item_needs"].delete_one({"_id": ObjectId(need_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item need not found")

    return {"message": "Item need deleted successfully"}


@router.get("/character/{character_id}/progress")
async def get_character_item_progress(character_id: str):
    """获取角色装备获取进度"""
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID")

    # 验证角色存在
    character = await db.get_database()["characters"].find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # 获取所有装备需求
    all_needs = await db.get_database()["item_needs"].find({"character_id": character_id}).to_list(length=100)

    total = len(all_needs)
    obtained = sum(1 for need in all_needs if need.get("obtained", False))

    return {
        "character_id": character_id,
        "character_name": character["name"],
        "total_needs": total,
        "obtained": obtained,
        "remaining": total - obtained,
        "progress_percentage": round((obtained / total * 100) if total > 0 else 0, 2)
    }