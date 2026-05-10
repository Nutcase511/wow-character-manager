from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class TalentTree(BaseModel):
    """天赋树模型"""
    id: Optional[int] = None
    class_name: str  # 职业名：牧师、法师等
    spec_name: str   # 天赋名：戒律、神圣、暗影
    spec_icon: Optional[str] = None  # 天赋图标
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TalentNode(BaseModel):
    """天赋节点模型"""
    id: Optional[int] = None
    tree_id: int     # 所属天赋树ID
    row: int         # 行位置 (1-11)
    col: int         # 列位置 (1-4)
    name: str        # 天赋名称
    icon: Optional[str] = None  # 图标URL
    max_points: int  # 最大点数
    description: Optional[str] = None  # 天赋描述
    requires: Optional[str] = None  # 前置天赋要求（JSON格式）
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TalentBuild(BaseModel):
    """天赋配点方案"""
    id: Optional[int] = None
    name: str        # 方案名称
    class_name: str  # 职业
    spec_name: str   # 主天赋
    points: Dict[str, int]  # 天赋点分配 {talent_node_id: points}
    image_path: Optional[str] = None  # 截图路径
    notes: Optional[str] = None  # 备注
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TalentTreeResponse(BaseModel):
    """天赋树完整响应（包含所有节点）"""
    tree: TalentTree
    nodes: List[TalentNode]


class TalentBuildCreate(BaseModel):
    """创建天赋配点请求"""
    name: str
    class_name: str
    spec_name: str
    points: Dict[str, int]
    notes: Optional[str] = None
