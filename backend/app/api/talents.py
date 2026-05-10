from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import sqlite3
import json
import os
import shutil
from datetime import datetime
from app.models.talent_models import (
    TalentTree, TalentNode, TalentBuild, 
    TalentTreeResponse, TalentBuildCreate
)
from app.core.database import db

router = APIRouter(prefix="/api/talents", tags=["talents"])


# ============ 职业和天赋配置 ============
WOW_CLASSES = {
    "priest": {"name": "牧师", "specs": ["戒律", "神圣", "暗影"], "icon": "class_priest"},
    "mage": {"name": "法师", "specs": ["奥术", "火焰", "冰霜"], "icon": "class_mage"},
    "warlock": {"name": "术士", "specs": ["痛苦", "恶魔学识", "毁灭"], "icon": "class_warlock"},
    "rogue": {"name": "潜行者", "specs": ["刺杀", "战斗", "敏锐"], "icon": "class_rogue"},
    "warrior": {"name": "战士", "specs": ["武器", "狂怒", "防护"], "icon": "class_warrior"},
    "hunter": {"name": "猎人", "specs": ["野兽控制", "射击", "生存"], "icon": "class_hunter"},
    "paladin": {"name": "圣骑士", "specs": ["神圣", "防护", "惩戒"], "icon": "class_paladin"},
    "shaman": {"name": "萨满祭司", "specs": ["元素", "增强", "恢复"], "icon": "class_shaman"},
    "druid": {"name": "德鲁伊", "specs": ["平衡", "野性战斗", "恢复"], "icon": "class_druid"},
    "deathknight": {"name": "死亡骑士", "specs": ["鲜血", "冰霜", "邪恶"], "icon": "class_deathknight"},
}


@router.get("/classes")
async def get_classes():
    """获取所有职业列表"""
    return {
        "classes": [
            {
                "id": key,
                "name": info["name"],
                "specs": info["specs"],
                "icon": info["icon"]
            }
            for key, info in WOW_CLASSES.items()
        ]
    }


@router.get("/trees/{class_name}")
async def get_class_talent_trees(class_name: str):
    """获取某职业的所有天赋树"""
    cursor = await db.execute(
        "SELECT * FROM talent_trees WHERE class_name = ? ORDER BY spec_name",
        (class_name,)
    )
    rows = await cursor.fetchall()
    
    trees = []
    for row in rows:
        trees.append({
            "id": row["id"],
            "class_name": row["class_name"],
            "spec_name": row["spec_name"],
            "spec_icon": row["spec_icon"],
            "description": row["description"]
        })
    
    return {"class_name": class_name, "trees": trees}


@router.get("/tree/{tree_id}")
async def get_talent_tree(tree_id: int):
    """获取完整天赋树（包含所有节点）"""
    # 获取天赋树信息
    cursor = await db.execute(
        "SELECT * FROM talent_trees WHERE id = ?",
        (tree_id,)
    )
    tree_row = await cursor.fetchone()
    
    if not tree_row:
        raise HTTPException(status_code=404, detail="Talent tree not found")
    
    # 获取所有天赋节点
    cursor = await db.execute(
        "SELECT * FROM talent_nodes WHERE tree_id = ? ORDER BY row, col",
        (tree_id,)
    )
    node_rows = await cursor.fetchall()
    
    tree = {
        "id": tree_row["id"],
        "class_name": tree_row["class_name"],
        "spec_name": tree_row["spec_name"],
        "spec_icon": tree_row["spec_icon"],
        "description": tree_row["description"]
    }
    
    nodes = []
    for row in node_rows:
        nodes.append({
            "id": row["id"],
            "tree_id": row["tree_id"],
            "row": row["row"],
            "col": row["col"],
            "name": row["name"],
            "icon": row["icon"],
            "max_points": row["max_points"],
            "description": row["description"],
            "requires": json.loads(row["requires"]) if row["requires"] else None
        })
    
    return {"tree": tree, "nodes": nodes}


@router.get("/tree/{class_name}/{spec_name}")
async def get_talent_tree_by_spec(class_name: str, spec_name: str):
    """通过职业和天赋名获取天赋树"""
    cursor = await db.execute(
        "SELECT id FROM talent_trees WHERE class_name = ? AND spec_name = ?",
        (class_name, spec_name)
    )
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Talent tree not found")
    
    return await get_talent_tree(row["id"])


# ============ 天赋配点方案 ============

@router.get("/builds")
async def get_talent_builds(
    class_name: Optional[str] = None,
    spec_name: Optional[str] = None
):
    """获取天赋配点方案列表"""
    query = "SELECT * FROM talent_builds WHERE 1=1"
    params = []
    
    if class_name:
        query += " AND class_name = ?"
        params.append(class_name)
    if spec_name:
        query += " AND spec_name = ?"
        params.append(spec_name)
    
    query += " ORDER BY created_at DESC"
    
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    
    builds = []
    for row in rows:
        builds.append({
            "id": row["id"],
            "name": row["name"],
            "class_name": row["class_name"],
            "spec_name": row["spec_name"],
            "points": json.loads(row["points"]),
            "image_path": row["image_path"],
            "notes": row["notes"],
            "created_at": row["created_at"]
        })
    
    return {"builds": builds}


@router.get("/builds/{build_id}")
async def get_talent_build(build_id: int):
    """获取单个天赋配点方案"""
    cursor = await db.execute(
        "SELECT * FROM talent_builds WHERE id = ?",
        (build_id,)
    )
    row = await cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Talent build not found")
    
    return {
        "id": row["id"],
        "name": row["name"],
        "class_name": row["class_name"],
        "spec_name": row["spec_name"],
        "points": json.loads(row["points"]),
        "image_path": row["image_path"],
        "notes": row["notes"],
        "created_at": row["created_at"]
    }


@router.post("/builds")
async def create_talent_build(build: TalentBuildCreate):
    """创建天赋配点方案"""
    cursor = await db.execute(
        """INSERT INTO talent_builds (name, class_name, spec_name, points, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (build.name, build.class_name, build.spec_name,
         json.dumps(build.points), build.notes,
         datetime.utcnow(), datetime.utcnow())
    )
    
    build_id = cursor.lastrowid
    return {"id": build_id, "message": "Talent build created successfully"}


@router.post("/builds/{build_id}/upload-image")
async def upload_build_image(build_id: int, file: UploadFile = File(...)):
    """上传天赋截图"""
    # 确保上传目录存在
    upload_dir = "uploads/talent_images"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1] or ".png"
    filename = f"talent_{build_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 更新数据库
    await db.execute(
        "UPDATE talent_builds SET image_path = ? WHERE id = ?",
        (file_path, build_id)
    )
    
    return {"image_path": file_path, "message": "Image uploaded successfully"}


@router.delete("/builds/{build_id}")
async def delete_talent_build(build_id: int):
    """删除天赋配点方案"""
    # 获取图片路径
    cursor = await db.execute(
        "SELECT image_path FROM talent_builds WHERE id = ?",
        (build_id,)
    )
    row = await cursor.fetchone()
    
    if row and row["image_path"]:
        # 删除图片文件
        try:
            os.remove(row["image_path"])
        except FileNotFoundError:
            pass
    
    # 删除数据库记录
    await db.execute("DELETE FROM talent_builds WHERE id = ?", (build_id,))
    
    return {"message": "Talent build deleted successfully"}


@router.post("/builds/{build_id}/save-image")
async def save_talent_image(build_id: int, image_data: dict):
    """保存Base64编码的天赋图片"""
    import base64
    
    # 确保上传目录存在
    upload_dir = "uploads/talent_images"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成文件名
    filename = f"talent_{build_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_path = os.path.join(upload_dir, filename)
    
    # 解码并保存Base64图片
    image_bytes = base64.b64decode(image_data["image"])
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    
    # 更新数据库
    await db.execute(
        "UPDATE talent_builds SET image_path = ? WHERE id = ?",
        (file_path, build_id)
    )
    
    return {"image_path": file_path, "message": "Image saved successfully"}
