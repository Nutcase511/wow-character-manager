from fastapi import APIRouter
from typing import List
from app.schemas.schemas import RealmResponse

router = APIRouter()

# 本地固定服务器列表（时光服）
LOCAL_REALMS = [
    {"id": 1, "name": "时光1", "slug": "shiguang1", "category": "CN", "locale": "zh_CN", "timezone": "Asia/Shanghai", "is_tournament": False, "region": "cn"},
    {"id": 2, "name": "时光2", "slug": "shiguang2", "category": "CN", "locale": "zh_CN", "timezone": "Asia/Shanghai", "is_tournament": False, "region": "cn"},
    {"id": 3, "name": "时光3", "slug": "shiguang3", "category": "CN", "locale": "zh_CN", "timezone": "Asia/Shanghai", "is_tournament": False, "region": "cn"},
    {"id": 4, "name": "时光4", "slug": "shiguang4", "category": "CN", "locale": "zh_CN", "timezone": "Asia/Shanghai", "is_tournament": False, "region": "cn"},
]


@router.get("/", response_model=List[RealmResponse])
async def get_realms():
    """获取本地服务器列表"""
    return [RealmResponse(**realm) for realm in LOCAL_REALMS]


@router.get("/{realm_slug}", response_model=RealmResponse)
async def get_realm(realm_slug: str):
    """获取指定服务器信息"""
    for realm in LOCAL_REALMS:
        if realm["slug"] == realm_slug or realm["name"] == realm_slug:
            return RealmResponse(**realm)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="服务器不存在")
