"""
暴雪API服务（已禁用）
所有数据从本地处理，不调用暴雪API
"""


class BlizzardAPIService:
    """暴雪API服务 - 本地模式，所有方法返回None"""

    async def get_item_details(self, item_id: int):
        return None

    async def get_item_icon(self, item_id: int):
        return None

    async def get_journal_instance(self, instance_id: int):
        return None

    async def get_journal_encounter(self, encounter_id: int):
        return None


blizzard_api = BlizzardAPIService()
