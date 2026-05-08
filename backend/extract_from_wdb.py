import os
import struct

def read_wdb_file(filepath):
    """读取WDB文件，提取装备数据"""
    items = {}
    
    try:
        with open(filepath, 'rb') as f:
            # WDB文件头
            header = f.read(12)
            if len(header) < 12:
                return items
            
            magic = header[:4].decode('ascii', errors='ignore')
            version = struct.unpack('<I', header[4:8])[0]
            build = struct.unpack('<I', header[8:12])[0]
            
            print(f"文件: {os.path.basename(filepath)}")
            print(f"  Magic: {magic}, Version: {version}, Build: {build}")
            
            # 读取记录
            offset = 12
            while True:
                # 读取记录头
                record_header = f.read(8)
                if len(record_header) < 8:
                    break
                
                record_id = struct.unpack('<I', record_header[:4])[0]
                record_size = struct.unpack('<I', record_header[4:8])[0]
                
                # 读取记录数据
                record_data = f.read(record_size)
                if len(record_data) < record_size:
                    break
                
                # 尝试提取名称（通常在记录的特定位置）
                try:
                    # 查找字符串（以null结尾）
                    name_start = record_data.find(b'\x00\x00') + 2
                    if name_start > 1:
                        name_end = record_data.find(b'\x00\x00', name_start)
                        if name_end > name_start:
                            name = record_data[name_start:name_end].decode('utf-16-le', errors='ignore')
                            if name and len(name) > 1 and len(name) < 100:
                                items[record_id] = name
                except:
                    pass
                
                offset += 8 + record_size
        
        print(f"  提取到 {len(items)} 条记录")
        return items
        
    except Exception as e:
        print(f"  读取失败: {e}")
        return items

def extract_from_cache(wow_path):
    """从游戏缓存中提取装备名称"""
    wdb_dir = os.path.join(wow_path, 'Cache', 'WDB', 'zhCN')
    
    if not os.path.exists(wdb_dir):
        print(f"WDB目录不存在: {wdb_dir}")
        return {}
    
    print(f"=== 正在从 {wdb_dir} 提取数据 ===")
    
    all_items = {}
    
    # 查找所有WDB文件
    for filename in os.listdir(wdb_dir):
        if filename.endswith('.wdb'):
            filepath = os.path.join(wdb_dir, filename)
            items = read_wdb_file(filepath)
            all_items.update(items)
    
    print(f"\n=== 总计提取到 {len(all_items)} 个物品 ===")
    
    # 保存到文件
    output_file = 'wow_items_from_game.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for item_id, name in sorted(all_items.items()):
            f.write(f"{item_id}|{name}\n")
    
    print(f"数据已保存到 {output_file}")
    return all_items

# 测试提取
if __name__ == '__main__':
    wow_path = r'C:\WOW\World of Warcraft\_classic_'
    extract_from_cache(wow_path)
