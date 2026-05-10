# -*- coding: utf-8 -*-
"""
角色数据刷新 API
整合多个数据源：tdInspect(装备/天赋/等级)、WCL(评分)
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.core.database import db
from app.core.config import settings
from datetime import datetime
import asyncio
import os
import sys
import json
import sqlite3

router = APIRouter()

# 导入 tdInspect 解析器
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _backend_dir)
from import_tdinspect import parse_tdinspect_lua, name_to_key, CLASS_ID_MAP_WOTLK, TDINSPECT_FILE


class RefreshResult(BaseModel):
    """刷新结果"""
    character_id: int
    character_name: str
    success: bool
    message: str
    updated_fields: List[str] = []
    errors: List[str] = []


class BatchRefreshResponse(BaseModel):
    """批量刷新响应"""
    success: bool
    message: str
    total: int
    success_count: int
    failed_count: int
    results: List[RefreshResult]


async def refresh_character_from_tdinspect(character_id: int, character_name: str) -> RefreshResult:
    """从 tdInspect 刷新单个角色的数据"""
    result = RefreshResult(
        character_id=character_id,
        character_name=character_name,
        success=False,
        message="",
        updated_fields=[],
        errors=[]
    )
    
    if not os.path.exists(TDINSPECT_FILE):
        result.errors.append("tdInspect 数据文件不存在")
        result.message = "tdInspect 数据文件不存在"
        return result
    
    try:
        # 解析 tdInspect 数据
        characters = parse_tdinspect_lua(TDINSPECT_FILE)
        
        # 查找匹配的角色
        char_key = name_to_key(character_name)
        matched_char = None
        
        for char in characters:
            if name_to_key(char["name"]) == char_key:
                matched_char = char
                break
        
        if not matched_char:
            result.errors.append(f"在 tdInspect 中未找到角色: {character_name}")
            result.message = "角色未在 tdInspect 中找到"
            return result
        
        # 准备更新数据
        updates = {}
        
        # 更新等级
        if matched_char.get("level"):
            updates["level"] = matched_char["level"]
            result.updated_fields.append("level")
        
        # 更新职业
        if matched_char.get("class"):
            char_class = CLASS_ID_MAP_WOTLK.get(matched_char["class"])
            if char_class:
                updates["wow_class"] = char_class
                result.updated_fields.append("wow_class")
        
        # 更新种族（如果有）
        if matched_char.get("race"):
            from import_tdinspect import RACE_ID_MAP
            race = RACE_ID_MAP.get(matched_char["race"])
            if race:
                updates["race"] = race
                result.updated_fields.append("race")
        
        # 更新天赋数据
        if matched_char.get("talents"):
            updates["talents_data"] = json.dumps(matched_char["talents"], ensure_ascii=False)
            result.updated_fields.append("talents_data")
        
        # 更新装备数据
        if matched_char.get("equips"):
            updates["equips_data"] = json.dumps(matched_char["equips"], ensure_ascii=False)
            result.updated_fields.append("equips_data")
        
        # 更新活跃天赋组
        if matched_char.get("activeGroup"):
            updates["active_talent_group"] = matched_char["activeGroup"]
            result.updated_fields.append("active_talent_group")
        
        # 执行数据库更新
        if updates:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            # 构建 UPDATE 语句
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [character_id]
            
            await db.execute(
                f"UPDATE characters SET {set_clause} WHERE id = ?",
                values
            )
            
            result.success = True
            result.message = f"成功更新 {len(result.updated_fields)} 个字段"
        else:
            result.message = "没有需要更新的数据"
            
    except Exception as e:
        result.errors.append(str(e))
        result.message = f"刷新失败: {str(e)}"
    
    return result


async def refresh_all_characters_from_tdinspect() -> BatchRefreshResponse:
    """从 tdInspect 刷新所有角色的数据"""
    # 获取所有角色
    rows = await db.fetchall("SELECT id, name FROM characters ORDER BY id")
    
    results = []
    success_count = 0
    failed_count = 0
    
    for row in rows:
        result = await refresh_character_from_tdinspect(row["id"], row["name"])
        results.append(result)
        
        if result.success:
            success_count += 1
        else:
            failed_count += 1
    
    return BatchRefreshResponse(
        success=True,
        message=f"刷新完成: {success_count} 成功, {failed_count} 失败",
        total=len(rows),
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )


@router.post("/refresh-all", response_model=BatchRefreshResponse)
async def refresh_all_characters():
    """
    刷新所有角色的数据
    从 tdInspect 获取：等级、职业、天赋、装备
    """
    try:
        return await refresh_all_characters_from_tdinspect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_id}/refresh", response_model=RefreshResult)
async def refresh_single_character(character_id: int):
    """
    刷新单个角色的数据
    从 tdInspect 获取：等级、职业、天赋、装备
    """
    # 获取角色信息
    row = await db.fetchone("SELECT id, name FROM characters WHERE id = ?", (character_id,))
    if not row:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    try:
        result = await refresh_character_from_tdinspect(row["id"], row["name"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-levels")
async def refresh_character_levels():
    """
    从 tdInspect 同步角色等级（保持向后兼容）
    """
    if not os.path.exists(TDINSPECT_FILE):
        raise HTTPException(status_code=404, detail="未找到tdInspect数据文件")
    
    try:
        characters = parse_tdinspect_lua(TDINSPECT_FILE)
        
        updated = 0
        skipped = 0
        
        for char in characters:
            char_key = name_to_key(char["name"])
            char_level = char.get("level", 0)
            char_class_id = char.get("class")
            char_class = CLASS_ID_MAP_WOTLK.get(char_class_id) if char_class_id else None
            
            # 查找匹配的角色
            row = await db.fetchone(
                "SELECT id, level, wow_class FROM characters WHERE name LIKE ?",
                (f"{char_key}%",)
            )
            
            if row:
                updates = []
                values = []
                
                if char_level > 0 and row["level"] != char_level:
                    updates.append("level = ?")
                    values.append(char_level)
                
                if char_class and row["wow_class"] != char_class:
                    updates.append("wow_class = ?")
                    values.append(char_class)
                
                if updates:
                    updates.append("updated_at = ?")
                    values.append(datetime.utcnow().isoformat())
                    values.append(row["id"])
                    
                    await db.execute(
                        f"UPDATE characters SET {', '.join(updates)} WHERE id = ?",
                        values
                    )
                    updated += 1
                else:
                    skipped += 1
        
        return {
            "success": True,
            "message": f"同步完成！更新 {updated} 条，跳过 {skipped} 条",
            "updated": updated,
            "skipped": skipped
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
