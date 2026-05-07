"""
从Accountant插件数据中导入金币统计数据
数据来源：Accountant插件的SavedVariables文件
"""

import re
import sqlite3
import os
from datetime import datetime

# Accountant插件数据目录 - 根据实际情况修改
ADDON_DIR = r"C:\WOW\World of Warcraft\_classic_titan_\WTF\Account"
DATA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wow_character_manager.db")

# Accountant数据来源的中文映射
SOURCE_TITLES = {
    "TRAIN": "训练",
    "TAXI": "飞行",
    "TRADE": "交易",
    "AH": "拍卖行",
    "MERCH": "商人",
    "REPAIRS": "修理",
    "MAIL": "邮件",
    "QUEST": "任务",
    "LOOT": "拾取",
    "OTHER": "其他",
    "VOID": "虚空仓库",
    "TRANSMO": "幻化",
    "Garrison": "要塞",
    "LFG": "随机副本",
    "Hair": "理发"
}

TIME_MODES = ["Session", "Day", "Week", "Total"]


def parse_lua_file(file_path):
    """
    解析Accountant的SavedVariables Lua文件
    返回解析后的数据结构
    """
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找Accountant_SaveData定义
    pattern = r'Accountant_SaveData\s*=\s*(\{.*\})\s*$'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"未找到Accountant_SaveData数据: {file_path}")
        return None

    # 简单的Lua table到Python dict的转换
    try:
        # 使用简单的解析方法
        data_str = match.group(1)
        # 将Lua table转换为Python可解析的格式
        # 这是一个简化版本，适用于Accountant的数据结构
        data = parse_lua_table(data_str)
        return data
    except Exception as e:
        print(f"解析Lua数据失败: {e}")
        return None


def parse_lua_table(s):
    """
    简单的Lua table解析器
    """
    # 清理和简化
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1].strip()
    
    result = {}
    current_key = None
    current_value = None
    depth = 0
    buffer = []
    
    i = 0
    while i < len(s):
        char = s[i]
        
        if char == '{':
            depth += 1
            buffer.append(char)
        elif char == '}':
            depth -= 1
            buffer.append(char)
            if depth == 0:
                if current_key is not None:
                    value_str = ''.join(buffer)
                    result[current_key] = parse_lua_table(value_str)
                    current_key = None
                    buffer = []
        elif char == '=' and depth == 0 and current_key is None:
            # 键值对分隔符
            key_str = ''.join(buffer).strip()
            key_str = key_str.strip('[]"\'')
            current_key = key_str
            buffer = []
        elif char == ',' and depth == 0:
            # 元素分隔符
            if current_key is not None:
                value_str = ''.join(buffer).strip()
                result[current_key] = parse_lua_value(value_str)
                current_key = None
                buffer = []
            elif buffer:
                # 数组元素
                value_str = ''.join(buffer).strip()
                if value_str:
                    if not isinstance(result, list):
                        result = []
                    result.append(parse_lua_value(value_str))
                buffer = []
        else:
            buffer.append(char)
        i += 1
    
    # 处理最后一个元素
    if current_key is not None and buffer:
        value_str = ''.join(buffer).strip()
        result[current_key] = parse_lua_value(value_str)
    elif buffer and not isinstance(result, list):
        value_str = ''.join(buffer).strip()
        if value_str:
            result = parse_lua_value(value_str)
    
    return result


def parse_lua_value(s):
    """
    解析Lua值
    """
    s = s.strip()
    if not s:
        return None
    
    # 字符串
    if s.startswith('"') and s.endswith('"') or s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    
    # 数字
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        pass
    
    # 布尔值
    if s.lower() == 'true':
        return True
    if s.lower() == 'false':
        return False
    
    # nil
    if s.lower() == 'nil':
        return None
    
    # 嵌套table
    if s.startswith('{'):
        return parse_lua_table(s)
    
    return s


def find_accountant_files(account_dir):
    """
    在账户目录中查找所有Accountant SavedVariables文件
    """
    accountant_files = []
    
    if not os.path.exists(account_dir):
        print(f"账户目录不存在: {account_dir}")
        return accountant_files
    
    # 遍历账户目录
    for root, dirs, files in os.walk(account_dir):
        for file in files:
            if file == "Accountant.lua":
                accountant_files.append(os.path.join(root, file))
    
    return accountant_files


def import_accountant_data(accountant_data, db_path):
    """
    将Accountant数据导入到数据库
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported_chars = 0
    imported_trans = 0
    
    try:
        # 遍历服务器
        if not isinstance(accountant_data, dict):
            print("数据格式错误，期望dict")
            return 0, 0
        
        for realm_name, realm_data in accountant_data.items():
            if not isinstance(realm_data, dict):
                continue
            
            # 遍历角色
            for char_name, char_data in realm_data.items():
                if not isinstance(char_data, dict):
                    continue
                
                print(f"\n处理角色: {char_name} - {realm_name}")
                
                # 查找或创建角色
                character_id = get_or_create_character(cursor, char_name, realm_name)
                
                if character_id:
                    # 导入金币数据
                    options = char_data.get("options", {})
                    data = char_data.get("data", {})
                    
                    # 更新当前金币
                    total_cash = options.get("totalcash", 0)
                    update_character_gold(cursor, character_id, char_name, realm_name, total_cash)
                    
                    # 导入交易数据
                    trans_count = import_transactions(cursor, character_id, data)
                    
                    imported_chars += 1
                    imported_trans += trans_count
                    print(f"  导入 {trans_count} 条交易记录")
        
        conn.commit()
        print(f"\n导入完成！")
        print(f"  角色数: {imported_chars}")
        print(f"  交易记录: {imported_trans}")
        
    except Exception as e:
        print(f"导入失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    return imported_chars, imported_trans


def get_or_create_character(cursor, name, realm):
    """
    获取或创建角色
    """
    cursor.execute("SELECT id FROM characters WHERE name = ? AND realm = ?", (name, realm))
    row = cursor.fetchone()
    
    if row:
        return row[0]
    
    # 创建新角色
    cursor.execute("""
        INSERT INTO characters (name, realm, wow_class, level, faction)
        VALUES (?, ?, ?, ?, ?)
    """, (name, realm, "未知", 80, "未知"))
    
    return cursor.lastrowid


def update_character_gold(cursor, character_id, char_name, realm, gold_copper):
    """
    更新角色当前金币
    """
    # 检查是否存在
    cursor.execute("SELECT id FROM character_gold WHERE character_id = ?", (character_id,))
    
    if cursor.fetchone():
        cursor.execute("""
            UPDATE character_gold
            SET current_gold = ?, last_updated = CURRENT_TIMESTAMP
            WHERE character_id = ?
        """, (gold_copper, character_id))
    else:
        cursor.execute("""
            INSERT INTO character_gold (character_id, character_name, realm, current_gold)
            VALUES (?, ?, ?, ?)
        """, (character_id, char_name, realm, gold_copper))
    
    # 添加快照
    cursor.execute("""
        INSERT INTO gold_snapshot (character_id, gold_amount)
        VALUES (?, ?)
    """, (character_id, gold_copper))


def import_transactions(cursor, character_id, data):
    """
    导入交易数据
    """
    count = 0
    
    if not isinstance(data, dict):
        return count
    
    # 删除旧数据
    cursor.execute("DELETE FROM gold_transaction WHERE character_id = ?", (character_id,))
    
    for source_key, source_data in data.items():
        if not isinstance(source_data, dict):
            continue
        
        source_title = SOURCE_TITLES.get(source_key, source_key)
        
        for time_mode in TIME_MODES:
            mode_data = source_data.get(time_mode, {})
            if not isinstance(mode_data, dict):
                continue
            
            amount_in = mode_data.get("In", 0)
            amount_out = mode_data.get("Out", 0)
            
            if amount_in > 0 or amount_out > 0:
                cursor.execute("""
                    INSERT INTO gold_transaction 
                    (character_id, source, source_title, time_mode, amount_in, amount_out)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (character_id, source_key, source_title, time_mode, amount_in, amount_out))
                count += 1
    
    return count


def format_gold(copper):
    """
    格式化金币显示
    """
    if copper is None:
        return "0 G 0 S 0 C"
    
    gold = copper // 10000
    silver = (copper % 10000) // 100
    copper = copper % 100
    
    return f"{gold} G {silver} S {copper} C"


def main():
    print("=" * 60)
    print("Accountant 金币数据导入工具")
    print("=" * 60)
    
    # 查找Accountant文件
    print(f"\n正在搜索Accountant数据文件...")
    print(f"搜索目录: {ADDON_DIR}")
    
    accountant_files = find_accountant_files(ADDON_DIR)
    
    if not accountant_files:
        print("\n未找到Accountant数据文件！")
        print("请确认:")
        print("1. Accountant插件已正确安装")
        print("2. 已登录过游戏并保存过数据")
        print("3. ADDON_DIR路径配置正确")
        return
    
    print(f"\n找到 {len(accountant_files)} 个Accountant数据文件:")
    for i, f in enumerate(accountant_files, 1):
        print(f"  {i}. {f}")
    
    # 处理每个文件
    total_chars = 0
    total_trans = 0
    
    for file_path in accountant_files:
        print(f"\n处理文件: {file_path}")
        data = parse_lua_file(file_path)
        
        if data:
            chars, trans = import_accountant_data(data, DATA_DB)
            total_chars += chars
            total_trans += trans
    
    print(f"\n" + "=" * 60)
    print(f"总计:")
    print(f"  角色: {total_chars}")
    print(f"  交易: {total_trans}")
    print("=" * 60)


if __name__ == "__main__":
    main()
