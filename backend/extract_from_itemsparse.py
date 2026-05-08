import os
import struct

def read_itemsparse_file(filepath):
    """读取ItemSparse文件，提取装备数据"""
    items = {}
    
    try:
        with open(filepath, 'rb') as f:
            # 读取文件大小
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(0)
            
            if file_size < 20:
                return items
            
            # 读取头部
            header = f.read(20)
            magic = header[:4].decode('ascii', errors='ignore')
            
            # 尝试解析不同格式
            if magic in ['WDC4', 'WDC3']:
                # WDC格式
                version = struct.unpack('<I', header[4:8])[0]
                record_count = struct.unpack('<I', header[8:12])[0]
                field_count = struct.unpack('<I', header[12:16])[0]
                string_table_size = struct.unpack('<I', header[16:20])[0]
                
                print(f"  WDC格式, 记录数: {record_count}, 字段数: {field_count}")
                
                # 跳过字段定义
                offset = 20
                for _ in range(field_count):
                    field_header = f.read(12)
                    offset += 12
                
                # 读取字符串表
                f.seek(file_size - string_table_size)
                string_table = f.read(string_table_size)
                
                # 读取记录
                f.seek(offset)
                for _ in range(record_count):
                    # 读取记录头
                    record_header = f.read(8)
                    if len(record_header) < 8:
                        break
                    
                    record_id = struct.unpack('<I', record_header[:4])[0]
                    record_offset = struct.unpack('<I', record_header[4:8])[0]
                    
                    # 读取记录数据
                    original_pos = f.tell()
                    f.seek(offset + record_offset)
                    
                    # 查找名称字符串偏移
                    name_offset_data = f.read(4)
                    if len(name_offset_data) == 4:
                        name_offset = struct.unpack('<I', name_offset_data)[0]
                        
                        # 从字符串表读取名称
                        if name_offset < len(string_table):
                            name_end = string_table.find(b'\x00', name_offset)
                            if name_end > name_offset:
                                name = string_table[name_offset:name_end].decode('utf-8', errors='ignore')
                                if name and len(name) > 1 and len(name) < 100:
                                    items[record_id] = name
                    
                    f.seek(original_pos + 8)
            
            else:
                # 尝试直接查找字符串
                data = f.read()
                # 查找UTF-8字符串（中文）
                i = 0
                while i < len(data):
                    if data[i] > 127:  # 中文开始
                        j = i
                        while j < len(data) and (data[j] > 127 or (data[j] >= 32 and data[j] <= 126)):
                            j += 1
                        if j - i > 1 and j - i < 100:
                            try:
                                name = data[i:j].decode('utf-8')
                                # 查找附近的数字作为item_id
                                num_start = max(0, i - 20)
                                num_end = min(len(data), i + 5)
                                num_data = data[num_start:num_end]
                                for k in range(len(num_data) - 3):
                                    if num_data[k:k+4].isdigit():
                                        item_id = int(num_data[k:k+4])
                                        items[item_id] = name
                                        break
                            except:
                                pass
                        i = j
                    i += 1
        
        return items
        
    except Exception as e:
        print(f"  读取失败: {e}")
        return items

def extract_from_adb(wow_path):
    """从ADB缓存中提取装备名称"""
    adb_dir = os.path.join(wow_path, 'Cache', 'ADB', 'zhCN')
    
    if not os.path.exists(adb_dir):
        print(f"ADB目录不存在: {adb_dir}")
        return {}
    
    print(f"=== 正在从 {adb_dir} 提取装备数据 ===")
    
    all_items = {}
    
    # 查找所有ItemSparse文件
    for filename in os.listdir(adb_dir):
        if filename.startswith('ItemSparse') and filename.endswith('.tmp'):
            filepath = os.path.join(adb_dir, filename)
            print(f"文件: {filename}")
            items = read_itemsparse_file(filepath)
            all_items.update(items)
            print(f"  提取到 {len(items)} 条记录")
    
    print(f"\n=== 总计提取到 {len(all_items)} 个装备 ===")
    
    # 保存到文件
    output_file = 'wow_items_from_adb.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for item_id, name in sorted(all_items.items()):
            f.write(f"{item_id}|{name}\n")
    
    print(f"数据已保存到 {output_file}")
    return all_items

# 测试提取
if __name__ == '__main__':
    wow_path = r'C:\WOW\World of Warcraft\_classic_'
    extract_from_adb(wow_path)
