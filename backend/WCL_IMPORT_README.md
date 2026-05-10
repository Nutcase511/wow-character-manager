# WCL 数据导入工具使用说明

## 概述

由于 WCL API 不支持时光服数据，本工具提供了一种手动导入 WCL 评分数据的方式。

## 使用步骤

### 方法一：从浏览器复制数据（推荐）

1. **打开 WCL 网页**
   - 访问 https://cn.classic.warcraftlogs.com/
   - 搜索你的角色（如：温小馨）
   - 进入角色详情页面

2. **打开开发者工具**
   - 按 `F12` 打开浏览器开发者工具
   - 切换到 `Network` (网络) 标签

3. **刷新页面**
   - 按 `F5` 刷新页面
   - 等待页面加载完成

4. **找到数据请求**
   - 在 Network 列表中查找包含 `character` 或 `rankings` 的请求
   - 通常 URL 类似于：`https://cn.classic.warcraftlogs.com/character/rankings/...`

5. **复制响应数据**
   - 点击该请求
   - 切换到 `Response` (响应) 标签
   - 右键点击响应内容
   - 选择 `Copy` -> `Copy response`

6. **运行导入工具**
   ```bash
   cd C:\wow后台管理\wow-character-manager\backend
   python import_wcl_data.py
   ```

7. **粘贴数据**
   - 将复制的数据粘贴到命令行
   - 输入 `END` 结束输入
   - 按提示确认导入

### 方法二：从文件导入

1. 将复制的数据保存为文本文件（如 `wcl_data.txt`）

2. 运行导入命令：
   ```bash
   python import_wcl_data.py wcl_data.txt
   ```

## 数据格式

工具支持以下数据格式：

### JSON 格式（推荐）
```json
{
  "character": {
    "id": 12345678,
    "name": "角色名",
    "server": {"name": "服务器名"},
    "class": "职业",
    "spec": "专精",
    "itemLevel": 245
  },
  "zoneRankings": {
    "1015": {
      "zoneName": "副本名",
      "bestPerformance": 85.5,
      "medianPerformance": 72.3
    }
  },
  "rankings": [...]
}
```

### HTML 格式
如果从页面源代码复制，工具也会尝试解析其中的 JSON 数据。

## 导入的数据字段

导入后，以下字段会被更新到数据库：

| 字段 | 说明 |
|------|------|
| `wcl_character_id` | WCL 角色 ID |
| `wcl_updated_at` | 数据更新时间 |
| `wcl_zone_rankings` | 副本评分数据（JSON） |
| `wcl_best_performances` | 最佳表现数据（JSON） |
| `wcl_item_level` | WCL 记录的装等 |
| `wcl_spec` | WCL 记录的专精 |
| `wcl_raw_data` | 原始数据备份 |

## 注意事项

1. **角色必须已存在**
   - 导入前请确保角色已通过 tdInspect 导入到数据库
   - 工具会根据角色名匹配数据库记录

2. **数据覆盖**
   - 导入会覆盖该角色已有的 WCL 数据
   - 原始数据会保留在 `wcl_raw_data` 字段中

3. **编码问题**
   - 确保复制的数据是 UTF-8 编码
   - 中文角色名和服务器名支持正常

## 故障排除

### 问题：无法解析数据

**解决方案：**
1. 确保复制的是完整的 JSON 响应
2. 检查是否包含了 `character` 或 `rankings` 字段
3. 尝试保存为文件后再导入

### 问题：角色未找到

**解决方案：**
1. 确认角色名与数据库中的记录一致
2. 检查是否有空格或特殊字符
3. 先通过 tdInspect 导入角色基础信息

### 问题：中文显示乱码

**解决方案：**
1. 确保命令行使用 UTF-8 编码：
   ```bash
   chcp 65001
   ```
2. 使用支持 UTF-8 的终端（如 Windows Terminal）

## 相关文件

- `wcl_data_parser.py` - 数据解析核心模块
- `import_wcl_data.py` - 导入工具主程序
- `example_wcl_import.py` - 使用示例

## 后续计划

- [ ] 开发浏览器扩展，一键导入 WCL 数据
- [ ] 支持自动同步 WCL 数据
- [ ] 添加数据可视化展示
