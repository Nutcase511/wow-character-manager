from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.schemas import RealmResponse
from app.services.blizzard_api import blizzard_api

router = APIRouter()


@router.get("/", response_model=List[RealmResponse])
async def get_realms(
    classic: bool = Query(False, description="是否获取怀旧服服务器列表"),
    region: Optional[str] = Query(None, description="服务器区域（us, eu, kr, tw, cn）")
):
    """获取服务器列表

    Args:
        classic: 是否获取怀旧服（时光服）服务器列表
        region: 服务器区域，不指定则使用配置文件中的默认区域

    Returns:
        服务器列表，包含服务器ID、名称、slug等信息
    """
    try:
        # 如果指定了区域，临时修改region（注意：这需要在服务端实现region切换）
        # 当前简化处理，使用配置的region

        realms = await blizzard_api.get_realms(classic=classic)

        if not realms:
            return []

        # 如果指定了region过滤
        if region:
            realms = [realm for realm in realms if realm.get("region") == region.lower()]

        return [RealmResponse(**realm) for realm in realms]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务器列表失败: {str(e)}")


@router.get("/{realm_slug}", response_model=RealmResponse)
async def get_realm(
    realm_slug: str,
    classic: bool = Query(False, description="是否为怀旧服服务器")
):
    """获取指定服务器信息

    Args:
        realm_slug: 服务器slug（如: "stormrage", "月神殿"等）
        classic: 是否为怀旧服服务器

    Returns:
        服务器详细信息
    """
    try:
        realm = await blizzard_api.get_realm(realm_slug, classic=classic)

        if not realm:
            raise HTTPException(status_code=404, detail="服务器不存在")

        return RealmResponse(**realm)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务器信息失败: {str(e)}")


@router.get("/classic/list", response_model=List[RealmResponse])
async def get_classic_realms(
    region: Optional[str] = Query(None, description="服务器区域")
):
    """获取怀旧服（时光服）服务器列表

    这是获取怀旧服服务器的快捷端点
    """
    return await get_realms(classic=True, region=region)


@router.get("/retail/list", response_model=List[RealmResponse])
async def get_retail_realms(
    region: Optional[str] = Query(None, description="服务器区域")
):
    """获取正式服服务器列表

    这是获取正式服服务器的快捷端点
    """
    return await get_realms(classic=False, region=region)