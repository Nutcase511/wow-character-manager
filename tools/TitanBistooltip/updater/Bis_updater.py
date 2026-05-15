# bis_updater.py - 基于桌面版本修改，支持分文件存储
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import datetime
import re

class BISDatabaseUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("快跑兄弟BIS面板装备更新工具")
        self.root.geometry("650x700")
        self.root.resizable(False, False)
        
        # 数据目录路径（修改：从单一文件改为目录）
        self.data_dir = r"d:\World of Warcraft\_classic_titan_\Interface\AddOns\TitanBistooltip\data"
        
        # 职业名称中英文映射（双向）
        self.class_name_mapping = {
            "Death knight": "死亡骑士",
            "Druid": "德鲁伊",
            "Hunter": "猎人",
            "Mage": "法师",
            "Paladin": "圣骑士",
            "Priest": "牧师",
            "Rogue": "盗贼",
            "Shaman": "萨满祭司",
            "Warrior": "战士",
            "Warlock": "术士"
        }
        self.class_name_reverse = {v: k for k, v in self.class_name_mapping.items()}
        
        # 天赋名称中英文映射（双向）
        self.spec_name_mapping = {
            # 死亡骑士
            "Blood tank": "血坦",
            "Blood dps": "鲜血输出",
            "Frost": "冰霜",
            "Unholy": "邪恶",
            # 德鲁伊
            "Balance": "平衡",
            "Feral tank": "野性坦克",
            "Feral dps": "野性输出",
            "Restoration": "恢复",
            # 猎人
            "Beast mastery": "兽王",
            "Marksmanship": "射击",
            "Survival": "生存",
            # 法师
            "Arcane": "奥术",
            "Fire": "火焰",
            "Fire FFB": "火焰法",
            "Frost": "冰霜",
            # 圣骑士
            "Holy": "神圣",
            "Protection": "防护",
            "Retribution": "惩戒",
            # 牧师
            "Discipline": "戒律",
            "Holy": "神圣",
            "Shadow": "暗影",
            # 盗贼
            "Assassination": "刺杀",
            "Combat": "战斗",
            "Subtlety": "敏锐",
            # 萨满祭司
            "Elemental": "元素",
            "Enhancement": "增强",
            "Restoration": "恢复",
            # 战士
            "Arms": "武器",
            "Fury": "狂怒",
            "Protection": "防护",
            # 术士
            "Affliction": "痛苦",
            "Demonology": "恶魔",
            "Destruction": "毁灭"
        }
        self.spec_name_reverse = {v: k for k, v in self.spec_name_mapping.items()}
        
        # 槽位名称中英文映射（双向）
        self.slot_name_mapping = {
            "Head": "头部",
            "Neck": "颈部",
            "Shoulder": "肩部",
            "Back": "背部",
            "Chest": "胸部",
            "Wrist": "手腕",
            "Hands": "手部",
            "Waist": "腰部",
            "Legs": "腿部",
            "Feet": "脚部",
            "Finger": "手指",
            "Trinket": "饰品",
            "Weapon": "武器",
            "Off hand": "副手",
            "Relic": "远程"
        }
        self.slot_name_reverse = {v: k for k, v in self.slot_name_mapping.items()}
        
        # 预设数据（如果解析失败，使用这些数据）
        self.default_classes = {
            "Death knight": ["Blood tank", "Blood dps", "Frost", "Unholy"],
            "Druid": ["Balance", "Feral tank", "Feral dps", "Restoration"],
            "Hunter": ["Beast mastery", "Marksmanship", "Survival"],
            "Mage": ["Arcane", "Fire", "Fire FFB", "Frost"],
            "Paladin": ["Holy", "Protection", "Retribution"],
            "Priest": ["Discipline", "Holy", "Shadow"],
            "Rogue": ["Assassination", "Combat", "Subtlety"],
            "Shaman": ["Elemental", "Enhancement", "Restoration"],
            "Warrior": ["Arms", "Fury", "Protection"],
            "Warlock": ["Affliction", "Demonology", "Destruction"]
        }
        self.default_phases = ["PR", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11"]
        self.slots = ["Head", "Neck", "Shoulder", "Back", "Chest", "Wrist", "Hands", "Waist", "Legs", "Feet", "Finger", "Trinket", "Weapon", "Off hand", "Relic"]
        
        # 加载数据库结构
        self.classes = {}  # 解析后的职业-专精映射
        self.phases = []   # 解析后的阶段列表
        self.bis_data = {} # 完整BIS数据：{职业: {专精: {阶段: {槽位: {装备ID列表, enhs}}}}}
        self.current_items = []  # 存储当前槽位的1-6个装备ID
        self.current_enhs = []   # 存储当前槽位的附魔/宝石数据
        
        # 创建UI
        self.create_widgets()
        self.refresh_db()
    
    def get_spec_file_path(self, class_name, spec_name):
        """获取天赋数据文件路径"""
        return os.path.join(self.data_dir, class_name, f"{spec_name}.lua")
    
    def create_widgets(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="快跑兄弟BIS装备数据库更新工具", font=("SimHei", 16))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 数据目录显示
        ttk.Label(main_frame, text="数据目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar(value=self.data_dir)
        path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=50, state='readonly')
        path_entry.grid(row=1, column=1, columnspan=2, pady=5)
        
        # 职业选择
        ttk.Label(main_frame, text="选择职业:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(main_frame, textvariable=self.class_var, width=20)
        self.class_combo.grid(row=2, column=1, pady=5)
        self.class_combo.bind("<<ComboboxSelected>>", self.on_class_select)
        
        # 专精选择
        ttk.Label(main_frame, text="选择专精:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.spec_var = tk.StringVar()
        self.spec_combo = ttk.Combobox(main_frame, textvariable=self.spec_var, width=20)
        self.spec_combo.grid(row=3, column=1, pady=5)
        self.spec_combo.bind("<<ComboboxSelected>>", self.on_spec_select)
        
        # 阶段选择
        ttk.Label(main_frame, text="选择阶段:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.phase_var = tk.StringVar()
        self.phase_combo = ttk.Combobox(main_frame, textvariable=self.phase_var, width=20)
        self.phase_combo.grid(row=4, column=1, pady=5)
        self.phase_combo.bind("<<ComboboxSelected>>", self.on_phase_select)
        
        # 槽位选择
        ttk.Label(main_frame, text="选择槽位:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.slot_var = tk.StringVar()
        self.slot_combo = ttk.Combobox(main_frame, textvariable=self.slot_var, width=20)
        # 槽位显示中文
        chinese_slots = [self.slot_name_mapping.get(slot, slot) for slot in self.slots]
        self.slot_combo['values'] = chinese_slots
        self.slot_combo.grid(row=5, column=1, pady=5)
        self.slot_combo.bind("<<ComboboxSelected>>", self.on_slot_select)
        
        # 装备位置选择
        ttk.Label(main_frame, text="装备位置 (1-6):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.position_var = tk.StringVar(value="1")
        self.position_spin = ttk.Spinbox(main_frame, from_=1, to=6, textvariable=self.position_var, width=5)
        self.position_spin.grid(row=6, column=1, pady=5, sticky=tk.W)
        
        # 装备ID输入
        ttk.Label(main_frame, text="装备ID:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.item_id_var = tk.StringVar()
        self.item_id_entry = ttk.Entry(main_frame, textvariable=self.item_id_var, width=20)
        self.item_id_entry.grid(row=7, column=1, pady=5)
        
        # 当前装备ID显示
        ttk.Label(main_frame, text="当前装备ID:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.current_items_frame = ttk.Frame(main_frame)
        self.current_items_frame.grid(row=8, column=1, pady=5, sticky=tk.W)
        self.current_items_labels = []
        for i in range(6):
            label = ttk.Label(self.current_items_frame, text=f"{i+1}: -", width=15)
            label.pack(side=tk.TOP, anchor=tk.W)
            self.current_items_labels.append(label)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(btn_frame, text="刷新数据库", command=self.refresh_db, width=15)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        self.save_btn = ttk.Button(btn_frame, text="保存更改", command=self.save_changes, width=15)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # 备份按钮
        self.backup_btn = ttk.Button(btn_frame, text="备份数据库", command=self.backup_db, width=15)
        self.backup_btn.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        self.exit_btn = ttk.Button(btn_frame, text="退出", command=self.root.quit, width=15)
        self.exit_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="green")
        status_label.grid(row=10, column=0, columnspan=3)
        
        # 版本信息
        version_label = ttk.Label(main_frame, text="版本 3.0 (支持分文件存储)", font=("Arial", 8))
        version_label.grid(row=11, column=2, sticky=tk.E, pady=10)
    
    def backup_db(self):
        """备份所有数据库文件"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.data_dir, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 复制所有职业目录
            for class_name in os.listdir(self.data_dir):
                if class_name.startswith('backup_'):
                    continue
                class_dir = os.path.join(self.data_dir, class_name)
                if os.path.isdir(class_dir):
                    dest_dir = os.path.join(backup_dir, class_name)
                    shutil.copytree(class_dir, dest_dir)
            
            messagebox.showinfo("成功", f"数据库已备份至：\n{backup_dir}")
            self.status_var.set("备份成功")
        except Exception as e:
            messagebox.showerror("错误", f"备份失败：{str(e)}")
            self.status_var.set("备份失败")
    
    def refresh_db(self):
        """刷新数据库结构（完整解析）"""
        self.status_var.set("正在加载数据库...")
        try:
            # 保存当前选择
            current_class = self.class_var.get()
            current_spec = self.spec_var.get()
            current_phase = self.phase_var.get()
            current_slot = self.slot_var.get()
            
            self.load_db_structure()
            self.load_bis_data()
            
            # 更新UI，但保持当前选择
            # 更新职业（显示中文）
            class_list = list(self.classes.keys())
            chinese_class_list = [self.class_name_mapping.get(cls, cls) for cls in class_list]
            self.class_combo['values'] = chinese_class_list
            
            # 更新阶段
            self.phase_combo['values'] = self.phases
            
            # 更新槽位（显示中文）
            chinese_slots = [self.slot_name_mapping.get(slot, slot) for slot in self.slots]
            
            # 恢复当前选择
            self.class_var.set(current_class)
            self.phase_var.set(current_phase)
            self.slot_var.set(current_slot)
            
            # 更新专精列表为当前职业的专精列表
            # 中文转英文职业名
            class_name = self.class_name_reverse.get(current_class, current_class)
            # 获取该职业的专精
            specs = self.classes.get(class_name, self.default_classes.get(class_name, []))
            # 专精显示中文
            chinese_specs = [self.spec_name_mapping.get(spec, spec) for spec in specs]
            self.spec_combo['values'] = chinese_specs
            if chinese_specs:
                # 尝试设置为之前选择的专精，如果不存在则设置为第一个
                if current_spec in chinese_specs:
                    self.spec_var.set(current_spec)
                else:
                    self.spec_var.set(chinese_specs[0])
            
            # 更新当前装备ID显示
            self.update_current_items_display()
            
            self.status_var.set("数据库加载成功")
        except Exception as e:
            self.status_var.set(f"加载失败，使用默认数据：{str(e)}")
            # 使用默认数据
            self.classes = self.default_classes
            self.phases = self.default_phases
            self.bis_data = {}
            self.update_ui_with_defaults()
    
    def load_db_structure(self):
        """加载数据库结构：职业、专精、阶段"""
        self.classes = {}
        self.phases = self.default_phases
        self.slots = ["Head", "Neck", "Shoulder", "Back", "Chest", "Wrist", "Hands", "Waist", "Legs", "Feet", "Finger", "Trinket", "Weapon", "Off hand", "Relic"]
        
        # 遍历data目录，加载职业和专精
        if os.path.exists(self.data_dir):
            for class_name in os.listdir(self.data_dir):
                if class_name.startswith('backup_'):
                    continue
                class_dir = os.path.join(self.data_dir, class_name)
                if os.path.isdir(class_dir):
                    self.classes[class_name] = []
                    for spec_file in os.listdir(class_dir):
                        if spec_file.endswith('.lua'):
                            spec_name = spec_file[:-4]  # 移除.lua后缀
                            self.classes[class_name].append(spec_name)
        
        # 兜底：如果解析不到职业，用默认数据
        if not self.classes:
            self.classes = self.default_classes
    
    def load_bis_data(self):
        """加载完整的BIS数据（装备ID、附魔/宝石）"""
        self.bis_data = {}
        
        for class_name in self.classes:
            self.bis_data[class_name] = {}
            for spec in self.classes[class_name]:
                self.bis_data[class_name][spec] = {}
                for phase in self.phases:
                    self.bis_data[class_name][spec][phase] = {}
                    
                    # 从文件中解析数据
                    spec_file = self.get_spec_file_path(class_name, spec)
                    if os.path.exists(spec_file):
                        try:
                            with open(spec_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # 匹配BIS数据行：TitanBistooltip_Titan_bislists["职业"]["专精"]["阶段"][槽位序号] = { ... }
                            bis_data_lines = []
                            # 找到所有的BIS数据行的起始位置
                            start_pos = 0
                            while True:
                                # 查找下一个BIS数据行的起始位置
                                start = content.find('TitanBistooltip_Titan_bislists[', start_pos)
                                if start == -1:
                                    break
                                # 查找当前BIS数据行的结束位置
                                # 计算花括号的数量，确保找到完整的BIS数据行
                                brace_count = 0
                                found_start = False
                                end = start
                                for i in range(start, len(content)):
                                    if content[i] == '{':
                                        brace_count += 1
                                        found_start = True
                                    elif content[i] == '}':
                                        brace_count -= 1
                                        if found_start and brace_count == 0:
                                            end = i + 1
                                            break
                                # 提取完整的BIS数据行
                                bis_line = content[start:end]
                                bis_data_lines.append(bis_line)
                                # 更新起始位置
                                start_pos = end
                            
                            # 解析每条BIS数据行
                            for bis_line in bis_data_lines:
                                # 提取职业、专精、阶段和槽位序号
                                # 使用更简单的正则表达式，只提取到槽位序号和等号后的部分
                                header_pattern = re.compile(
                                    r'TitanBistooltip_Titan_bislists\["([^"\\]+)"\]\["([^"\\]+)"\]\["([^"\\]+)"\]\[(\d+)\]\s*=\s*\{(.*)\}',
                                    re.DOTALL
                                )
                                header_match = header_pattern.match(bis_line)
                                if header_match:
                                    line_class, line_spec, line_phase, slot_idx, full_content = header_match.groups()
                                    
                                    # 只处理当前职业、专精、阶段的数据，忽略专精名称的大小写
                                    if line_class != class_name or line_spec.lower() != spec.lower() or line_phase != phase:
                                        continue
                                    
                                    # 解析槽位名称
                                    slot_name_pattern = re.compile(r'\["slot_name"\]\s*=\s*"([^"\\]+)"')
                                    slot_name_match = slot_name_pattern.search(full_content)
                                    slot_name = slot_name_match.group(1) if slot_name_match else self.slots[int(slot_idx)-1]
                                    
                                    # 处理远程槽位的映射，将所有远程槽位统一映射为"远程"
                                    remote_slots = ["Relic", "Ranged", "Wand", "Totem", "Sigil", "Sanctified"]
                                    if slot_name in remote_slots:
                                        # 将所有远程槽位统一存储为"Relic"，以便在UI中显示为"远程"
                                        slot_name = "Relic"
                                    
                                    # 处理远程槽位的映射，确保所有远程槽位都能被正确识别
                                    remote_slots = ["Relic", "Ranged", "Wand", "Totem", "Sigil", "Sanctified"]
                                    if slot_name in remote_slots:
                                        # 为远程槽位创建映射，确保在UI中能正确显示
                                        if slot_name not in self.slot_name_mapping:
                                            self.slot_name_mapping[slot_name] = slot_name
                                        if slot_name not in self.slots:
                                            self.slots.append(slot_name)
                                    
                                    # 解析附魔/宝石（enhs）
                                    enhs = {}
                                    
                                    # 解析装备ID（1-6）
                                    item_ids = {}
                                    
                                    # 找到enhs部分的结束位置，确保只解析enhs之后的装备ID
                                    enhs_end = full_content.find('}, [1] =')
                                    if enhs_end == -1:
                                        # 如果找不到'}, [1] ='，尝试找到enhs部分的结束位置
                                        enhs_start = full_content.find('"enhs"')
                                        if enhs_start != -1:
                                            # 找到enhs部分的结束位置
                                            brace_count = 0
                                            found_start = False
                                            for j in range(enhs_start, len(full_content)):
                                                if full_content[j] == '{':
                                                    brace_count += 1
                                                    found_start = True
                                                elif full_content[j] == '}':
                                                    brace_count -= 1
                                                    if found_start and brace_count == 0:
                                                        enhs_end = j + 1
                                                        break
                                    
                                    # 从enhs结束位置开始解析装备ID
                                    parse_start = enhs_end if enhs_end != -1 else 0
                                    parse_str = full_content[parse_start:]
                                    
                                    # 解析装备ID
                                    for i in range(1, 7):
                                        # 构建搜索模式
                                        item_pattern = f'[{i}] = '
                                        item_pos = parse_str.find(item_pattern)
                                        
                                        if item_pos != -1:
                                            # 提取数字
                                            value_start = item_pos + len(item_pattern)
                                            value_end = parse_str.find(',', value_start)
                                            if value_end == -1:
                                                value_end = parse_str.find('}', value_start)
                                            
                                            if value_end != -1:
                                                item_id_str = parse_str[value_start:value_end].strip()
                                                if item_id_str.isdigit() or (item_id_str.startswith('-') and item_id_str[1:].isdigit()):
                                                    item_ids[i] = int(item_id_str)
                                                else:
                                                    item_ids[i] = -1
                                            else:
                                                item_ids[i] = -1
                                        else:
                                            item_ids[i] = -1
                                    
                                    # 存储数据
                                    self.bis_data[class_name][spec][phase][slot_name] = {
                                        "item_ids": item_ids,
                                        "enhs": enhs,
                                        "slot_idx": int(slot_idx)
                                    }
                        except Exception as e:
                            print(f"解析 {class_name}-{spec}-{phase} 失败: {str(e)}")
    
    def update_ui_with_defaults(self):
        """使用默认数据更新UI"""
        # 更新职业（显示中文）
        class_list = list(self.default_classes.keys())
        chinese_class_list = [self.class_name_mapping.get(cls, cls) for cls in class_list]
        self.class_combo['values'] = chinese_class_list
        if chinese_class_list:
            self.class_var.set(chinese_class_list[0])
            # 更新专精（显示中文）
            specs = self.default_classes[class_list[0]]
            chinese_specs = [self.spec_name_mapping.get(spec, spec) for spec in specs]
            self.spec_combo['values'] = chinese_specs
            if chinese_specs:
                self.spec_var.set(chinese_specs[0])
        # 更新阶段
        self.phase_combo['values'] = self.default_phases
        self.phase_var.set("P3" if "P3" in self.default_phases else self.default_phases[0])
        # 更新槽位（显示中文）
        chinese_slots = [self.slot_name_mapping.get(slot, slot) for slot in self.slots]
        self.slot_var.set(chinese_slots[0])
        # 更新当前装备ID显示
        self.update_current_items_display()
    
    def on_class_select(self, event=None):
        """职业选择事件"""
        chinese_class = self.class_var.get()
        class_name = self.class_name_reverse.get(chinese_class, chinese_class)
        
        if class_name in self.classes:
            specs = self.classes[class_name]
            chinese_specs = [self.spec_name_mapping.get(spec, spec) for spec in specs]
            self.spec_combo['values'] = chinese_specs
            if chinese_specs:
                self.spec_var.set(chinese_specs[0])
                self.update_current_items_display()
    
    def on_spec_select(self, event=None):
        """专精选择事件"""
        self.update_current_items_display()
    
    def on_phase_select(self, event=None):
        """阶段选择事件"""
        self.update_current_items_display()
    
    def on_slot_select(self, event=None):
        """槽位选择事件"""
        self.update_current_items_display()
    
    def update_current_items_display(self):
        """更新当前装备ID显示"""
        try:
            chinese_class = self.class_var.get()
            chinese_spec = self.spec_var.get()
            phase = self.phase_var.get()
            chinese_slot = self.slot_var.get()
            
            if chinese_class and chinese_spec and phase and chinese_slot:
                class_name = self.class_name_reverse.get(chinese_class, chinese_class)
                spec = self.spec_name_reverse.get(chinese_spec, chinese_spec)
                slot_name = self.slot_name_reverse.get(chinese_slot, chinese_slot)
                
                # 尝试匹配远程槽位
                if slot_name == "Relic":
                    for remote_slot in ["Relic", "Ranged", "Wand", "Totem", "Sigil", "Sanctified"]:
                        if (class_name in self.bis_data and 
                            spec in self.bis_data[class_name] and 
                            phase in self.bis_data[class_name][spec] and 
                            remote_slot in self.bis_data[class_name][spec][phase]):
                            slot_name = remote_slot
                            break
                
                if (class_name in self.bis_data and 
                    spec in self.bis_data[class_name] and 
                    phase in self.bis_data[class_name][spec] and 
                    slot_name in self.bis_data[class_name][spec][phase]):
                    slot_data = self.bis_data[class_name][spec][phase][slot_name]
                    item_ids = slot_data["item_ids"]
                    # 更新显示
                    for i in range(1, 7):
                        self.current_items_labels[i-1].config(text=f"{i}: {item_ids.get(i, -1)}")
                    # 保存当前装备ID列表
                    self.current_items = [item_ids.get(i, -1) for i in range(1, 7)]
                    self.current_enhs = slot_data.get("enhs", {})
                else:
                    # 无数据时初始化
                    self.current_items = [-1]*6
                    self.current_enhs = {}
            else:
                # 无数据时初始化
                self.current_items = [-1]*6
                self.current_enhs = {}
        except Exception as e:
            print(f"更新装备显示失败: {str(e)}")
            # 无数据时初始化
            self.current_items = [-1]*6
            self.current_enhs = {}
    
    def save_changes(self):
        """保存修改后的装备ID到数据库"""
        try:
            # 获取选中条件
            chinese_class = self.class_var.get()
            chinese_spec = self.spec_var.get()
            phase = self.phase_var.get()
            chinese_slot = self.slot_var.get()
            position = int(self.position_var.get())
            item_id = self.item_id_var.get().strip()
            
            # 验证输入
            if not item_id:
                messagebox.showwarning("警告", "装备ID不能为空")
                return
            if not item_id.lstrip('-').isdigit():
                messagebox.showwarning("警告", "装备ID必须是数字（可填-1表示无）")
                return
            item_id = int(item_id)
            
            # 中文转英文
            class_name = self.class_name_reverse.get(chinese_class, chinese_class)
            spec = self.spec_name_reverse.get(chinese_spec, chinese_spec)
            slot_name = self.slot_name_reverse.get(chinese_slot, chinese_slot)
            
            # 获取天赋数据文件路径
            spec_file = self.get_spec_file_path(class_name, spec)
            if not os.path.exists(spec_file):
                messagebox.showerror("错误", f"天赋数据文件不存在：{spec_file}")
                return
            
            # 1. 读取原文件内容
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 2. 找到对应槽位的行并替换装备ID
            # 先找槽位序号（通过slot_name反向查idx）
            slot_idx = None
            
            # 定义远程槽位的所有可能名称
            remote_slots = ["Relic", "Ranged", "Wand", "Totem", "Sigil", "Sanctified"]
            
            # 如果当前槽位是远程槽位，尝试匹配所有可能的远程槽位英文名称
            if slot_name == "Relic":
                for remote_slot in remote_slots:
                    # 使用不区分大小写的正则表达式，匹配专精名称
                    bis_pattern = rf'TitanBistooltip_Titan_bislists\["{re.escape(class_name)}"\]\["([^"\\]+)"\]\["{re.escape(phase)}"\]\[(\d+)\]\s*=\s*\{{[^}}]*\["slot_name"\]\s*=\s*"{re.escape(remote_slot)}"[^}}]*\}}'
                    bis_match = re.search(bis_pattern, content, re.DOTALL | re.IGNORECASE)
                    if bis_match:
                        # 检查匹配到的专精名称是否与当前专精名称（忽略大小写）一致
                        matched_spec = bis_match.group(1)
                        if matched_spec.lower() == spec.lower():
                            slot_idx = bis_match.group(2)
                            slot_name = remote_slot  # 更新为实际的槽位名称
                            break
            else:
                # 匹配普通槽位，使用不区分大小写的正则表达式
                bis_pattern = rf'TitanBistooltip_Titan_bislists\["{re.escape(class_name)}"\]\["([^"\\]+)"\]\["{re.escape(phase)}"\]\[(\d+)\]\s*=\s*\{{[^}}]*\["slot_name"\]\s*=\s*"{re.escape(slot_name)}"[^}}]*\}}'
                bis_match = re.search(bis_pattern, content, re.DOTALL | re.IGNORECASE)
                if bis_match:
                    # 检查匹配到的专精名称是否与当前专精名称（忽略大小写）一致
                    matched_spec = bis_match.group(1)
                    if matched_spec.lower() == spec.lower():
                        slot_idx = bis_match.group(2)
            
            if not slot_idx:
                messagebox.showerror("错误", f"未找到{chinese_class}-{chinese_spec}-{phase}-{chinese_slot}的配置行")
                return
            
            # 1. 找到整个BIS数据行的开始位置，使用不区分大小写的正则表达式
            bis_start_pattern = rf'TitanBistooltip_Titan_bislists\["{re.escape(class_name)}"\]\["([^"\\]+)"\]\["{re.escape(phase)}"\]\[{slot_idx}\]\s*=\s*\{{'
            bis_start_match = re.search(bis_start_pattern, content, re.IGNORECASE)
            if not bis_start_match:
                raise Exception(f"未找到{class_name}-{spec}-{phase}-{slot_name}的配置行")
            
            # 2. 找到整个BIS数据行的结束位置
            start_pos = bis_start_match.start()
            brace_count = 1
            end_pos = start_pos + len(bis_start_match.group(0))
            
            while end_pos < len(content) and brace_count > 0:
                if content[end_pos] == '{':
                    brace_count += 1
                elif content[end_pos] == '}':
                    brace_count -= 1
                end_pos += 1
            
            # 提取完整的BIS数据行
            bis_block = content[start_pos:end_pos]
            bis_start = start_pos
            bis_end = end_pos

            # 3. 找到enhs部分的结束位置
            enhs_pattern = r'\["enhs"\]\s*=\s*\{'
            enhs_start_match = re.search(enhs_pattern, bis_block)
            enhs_end_in_block = 0
            
            if enhs_start_match:
                # 找到enhs部分的结束位置
                enhs_start_pos = enhs_start_match.start()
                brace_count = 1
                enhs_end_pos = enhs_start_pos + len(enhs_start_match.group(0))
                
                while enhs_end_pos < len(bis_block) and brace_count > 0:
                    if bis_block[enhs_end_pos] == '{':
                        brace_count += 1
                    elif bis_block[enhs_end_pos] == '}':
                        brace_count -= 1
                    enhs_end_pos += 1
                
                enhs_end_in_block = enhs_end_pos

            # 4. 从enhs结束位置开始，找到装备ID部分
            search_in_block = bis_block[enhs_end_in_block:]
            equip_pattern = rf'\[{position}\]\s*=\s*(-?\d+)'
            equip_match = re.search(equip_pattern, search_in_block)

            if equip_match:
                # 计算在整个内容中的位置
                match_start = bis_start + enhs_end_in_block + equip_match.start(1)
                match_end = match_start + len(equip_match.group(1))
                # 替换装备ID
                new_content = content[:match_start] + str(item_id) + content[match_end:]
                print(f"DEBUG: 找到装备ID位置{position}，替换 {equip_match.group(1)} -> {item_id}")
                print(f"DEBUG: 替换位置: {match_start} - {match_end}")
            else:
                # 如果找不到，在装备ID部分的末尾追加
                insert_pos = bis_end - 1  # 在 } 之前插入
                append_str = f", [{position}] = {item_id}"
                new_content = content[:insert_pos] + append_str + content[insert_pos:]
                print(f"DEBUG: 未找到装备ID位置{position}，在位置{insert_pos}追加")
            
            # 检查new_content是否真的改变了
            if new_content == content:
                print("DEBUG: 警告！内容没有变化！")
            
            # 3. 写入文件
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # 4. 刷新数据，但保持当前选择
            current_class = self.class_var.get()
            current_spec = self.spec_var.get()
            current_phase = self.phase_var.get()
            current_slot = self.slot_var.get()
            
            self.refresh_db()
            
            self.class_var.set(current_class)
            self.spec_var.set(current_spec)
            self.phase_var.set(current_phase)
            self.slot_var.set(current_slot)
            
            self.update_current_items_display()
            
            messagebox.showinfo("成功", f"已保存：{chinese_class}-{chinese_spec}-{phase}-{chinese_slot} 位置{position} → {item_id}")
            self.status_var.set("保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
            self.status_var.set("保存失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = BISDatabaseUpdater(root)
    root.mainloop()