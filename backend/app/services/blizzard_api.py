import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
import base64
import time


class BlizzardAPIService:
    def __init__(self):
        self.client_id = settings.BLIZZARD_CLIENT_ID
        self.client_secret = settings.BLIZZARD_CLIENT_SECRET
        self.region = settings.BLIZZARD_REGION
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0
        self.base_url = f"https://{self.region}.api.blizzard.com"

    async def get_access_token(self) -> str:
        """获取暴雪API访问令牌"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        token_url = "https://oauth.battle.net/token"
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                headers=headers,
                data={"grant_type": "client_credentials"}
            )
            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            self.token_expires_at = time.time() + data["expires_in"] - 300  # 提前5分钟过期

            return self.access_token

    async def make_request(self, endpoint: str, params: Optional[Dict] = None, namespace: str = "static") -> Dict[str, Any]:
        """发起API请求"""
        token = await self.get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Battlenet-Namespace": f"{namespace}-{self.region}"
        }

        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_item_icon(self, item_id: int) -> Optional[str]:
        """获取装备图标URL"""
        try:
            data = await self.make_request(f"/data/wow/item/{item_id}")
            icon = data.get("media", [{}])[0].get("key", {}).get("href") if data.get("media") else None
            return icon
        except Exception as e:
            print(f"Error fetching item icon: {e}")
            return None

    async def get_item_details(self, item_id: int) -> Optional[Dict[str, Any]]:
        """获取装备详细信息"""
        try:
            data = await self.make_request(f"/data/wow/item/{item_id}")
            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "quality": data.get("quality", {}).get("type"),
                "level": data.get("level"),
                "item_class": data.get("item_class", {}).get("name"),
                "item_subclass": data.get("item_subclass", {}).get("name"),
                "inventory_type": data.get("inventory_type", {}).get("name"),
                "icon": data.get("media", [{}])[0].get("key", {}).get("href") if data.get("media") else None,
                "stats": self._parse_item_stats(data.get("stats", [])),
                "spells": data.get("spells", []),
                "source": data.get("source", {}).get("name")
            }
        except Exception as e:
            print(f"Error fetching item details: {e}")
            return None

    def _parse_item_stats(self, stats: List[Dict]) -> Dict[str, int]:
        """解析装备属性"""
        stat_mapping = {
            "STRENGTH": "力量",
            "AGILITY": "敏捷",
            "INTELLECT": "智力",
            "STAMINA": "耐力",
            "CRITICAL_STRIKE": "暴击",
            "HASTE": "急速",
            "MASTERY": "精通",
            "VERSATILITY": "全能",
            "CRITICAL_STRIKE_BONUS": "暴击等级",
            "HASTE_BONUS": "急速等级",
            "MASTERY_BONUS": "精通等级",
            "VERSATILITY_BONUS": "全能等级"
        }

        parsed_stats = {}
        for stat in stats:
            stat_type = stat.get("type", {}).get("type")
            stat_name = stat_mapping.get(stat_type, stat_type)
            if stat_name:
                parsed_stats[stat_name] = stat.get("value", 0)

        return parsed_stats

    async def get_journal_instance(self, instance_id: int) -> Optional[Dict[str, Any]]:
        """获取副本信息"""
        try:
            data = await self.make_request(f"/data/wow/journal-instance/{instance_id}")
            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "description": data.get("description"),
                "map": data.get("map", {}).get("name"),
                "area": data.get("area", {}).get("name"),
                "minimum_level": data.get("minimum_level"),
                "modes": data.get("modes", []),
                "icon": data.get("media", [{}])[0].get("key", {}).get("href") if data.get("media") else None
            }
        except Exception as e:
            print(f"Error fetching instance details: {e}")
            return None

    async def get_journal_encounter(self, encounter_id: int) -> Optional[Dict[str, Any]]:
        """获取Boss信息"""
        try:
            data = await self.make_request(f"/data/wow/journal-encounter/{encounter_id}")
            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "description": data.get("description"),
                "instance": data.get("instance", {}).get("name"),
                "category": data.get("category", {}).get("name"),
                "icon": data.get("media", [{}])[0].get("key", {}).get("href") if data.get("media") else None
            }
        except Exception as e:
            print(f"Error fetching encounter details: {e}")
            return None

    async def get_realms(self, classic: bool = False) -> Optional[List[Dict[str, Any]]]:
        """获取服务器列表

        Args:
            classic: 是否获取怀旧服服务器列表

        Returns:
            服务器列表，包含服务器ID、名称、区域等信息
        """
        try:
            # 怀旧服使用动态namespace
            namespace = "dynamic-classic" if classic else "dynamic"

            data = await self.make_request("/data/wow/realm/index", namespace=namespace)

            realms = []
            if data.get("realms"):
                for realm in data["realms"]:
                    realms.append({
                        "id": realm.get("id"),
                        "name": realm.get("name"),
                        "slug": realm.get("slug"),
                        "category": realm.get("category", {}).get("type"),
                        "locale": realm.get("locale"),
                        "timezone": realm.get("timezone"),
                        "is_tournament": realm.get("is_tournament", False),
                        "region": self.region
                    })

            return realms
        except Exception as e:
            print(f"Error fetching realms: {e}")
            return None

    async def get_realm(self, realm_slug: str, classic: bool = False) -> Optional[Dict[str, Any]]:
        """获取指定服务器信息

        Args:
            realm_slug: 服务器slug
            classic: 是否为怀旧服

        Returns:
            服务器详细信息
        """
        try:
            namespace = "dynamic-classic" if classic else "dynamic"
            data = await self.make_request(f"/data/wow/realm/{realm_slug}", namespace=namespace)

            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "slug": data.get("slug"),
                "category": data.get("category", {}).get("type"),
                "locale": data.get("locale"),
                "timezone": data.get("timezone"),
                "connected_realm": data.get("connected_realm", {}).get("href"),
                "is_tournament": data.get("is_tournament", False),
                "region": self.region
            }
        except Exception as e:
            print(f"Error fetching realm details: {e}")
            return None


blizzard_api = BlizzardAPIService()