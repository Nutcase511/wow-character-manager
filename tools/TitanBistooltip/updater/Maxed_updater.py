import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import datetime
import re

class MaxedDatabaseUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("快跑兄弟毕业装框架更新工具")
        self.root.geometry("650x600")
        self.root.resizable(False, False)
        
        # 数据库文件路径
        self.db_path = r"d:\World of Warcraft\_classic_titan_\Interface\AddOns\TitanBistooltip\TitanBistooltip_Maxed_bislists.lua"
        # Maxed数据文件夹路径
        self.maxed_data_dir = r"d:\World of Warcraft\_classic_titan_\Interface\AddOns\TitanBistooltip\maxed"
        
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
            "Fire FFB": "霜火法",
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
            "Finger": "戒指",
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
        
        # 可穿戴两个的装备
        self.double_slots = ["Finger", "Trinket"]
        
        # 加载数据库结构
        self.classes = {}  # 解析后的职业-专精映射
        self.phases = []   # 解析后的阶段列表
        self.maxed_data = {} # 完整毕业装备数据：{职业: {专精: {阶段: {槽位: {装备ID列表, enhs}}}}}
        self.current_items = []  # 存储当前槽位的1-2个装备ID
        self.current_enhs = []   # 存储当前槽位的附魔/宝石数据
        
        # 创建UI
        self.create_widgets()
        self.refresh_db()
    
    def create_widgets(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="毕业装备更新工具", font=("SimHei", 16))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 数据库路径
        ttk.Label(main_frame, text="数据库路径:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar(value=self.db_path)
        path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=40)
        path_entry.grid(row=1, column=1, pady=5)
        browse_btn = ttk.Button(main_frame, text="浏览", command=self.browse_path, width=10)
        browse_btn.grid(row=1, column=2, pady=5)
        
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
        ttk.Label(main_frame, text="装备位置 (1-2):").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.position_var = tk.StringVar(value="1")
        self.position_spin = ttk.Spinbox(main_frame, from_=1, to=2, textvariable=self.position_var, width=5)
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
        for i in range(2):
            label = ttk.Label(self.current_items_frame, text=f"{i+1}: -", width=15)
            label.pack(side=tk.TOP, anchor=tk.W)
            self.current_items_labels.append(label)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        # 保存按钮
        save_btn = ttk.Button(btn_frame, text="保存更改", command=self.save_changes, width=15)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 备份按钮
        backup_btn = ttk.Button(btn_frame, text="备份数据库", command=self.backup_db, width=15)
        backup_btn.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        exit_btn = ttk.Button(btn_frame, text="退出", command=self.root.quit, width=15)
        exit_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="green")
        status_label.grid(row=10, column=0, columnspan=3)
        
        # 快跑提醒
        warning_label = ttk.Label(main_frame, text="快跑提醒：戒指和饰品的装备1和装备2都有效，因为有两个部件，其它的部位只有装备1有效，装备2是为了占位。", foreground="red", font=('SimHei', 9))
        warning_label.grid(row=11, column=0, columnspan=3, pady=10)
    
    def browse_path(self):
        """浏览文件路径"""
        file_path = filedialog.askopenfilename(
            title="选择数据库文件",
            filetypes=[("Lua文件", "*.lua"), ("所有文件", "*.*")]
        )
        if file_path:
            self.path_var.set(file_path)
            self.db_path = file_path
            self.refresh_db()
    
    def backup_db(self):
        """备份数据库"""
        if not os.path.exists(self.db_path):
            messagebox.showerror("错误", "数据库文件不存在")
            return
        
        backup_path = f"{self.db_path}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.lua"
        try:
            shutil.copy2(self.db_path, backup_path)
            messagebox.showinfo("成功", f"数据库已备份至:\n{backup_path}")
            self.status_var.set("备份成功")
        except Exception as e:
            messagebox.showerror("错误", f"备份失败: {str(e)}")
            self.status_var.set("备份失败")
    
    def refresh_db(self):
        """刷新数据库结构"""
        print("开始加载毕业装备数据...")
        try:
            # 重置数据结构
            self.classes = {}
            self.phases = []
            self.maxed_data = {}
            
            # 使用默认数据
            print("使用默认数据结构")
            self.classes = self.default_classes
            self.phases = self.default_phases
            
            # 从maxed文件夹读取数据
            if os.path.exists(self.maxed_data_dir):
                for class_name in self.default_classes.keys():
                    class_dir = os.path.join(self.maxed_data_dir, class_name)
                    if os.path.exists(class_dir):
                        for spec in self.default_classes[class_name]:
                            spec_file = os.path.join(class_dir, f"{spec}.lua")
                            if os.path.exists(spec_file):
                                with open(spec_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # 解析文件内容
                                lines = content.split('\n')
                                for line in lines:
                                    line = line.strip()
                                    if not line or 'TitanBistooltip_Maxed_bislists' not in line:
                                        continue
                                    
                                    # 尝试匹配装备数据行
                                    import re
                                    pattern = r'TitanBistooltip_Maxed_bislists\["([^"]+)"\]\["([^"]+)"\]\["([^"]+)"\]\[([0-9]+)\] = \{ \["slot_name"\] = "([^"]+)", \["enhs"\] = \{ [^\}]*\}, \[1\] = ([0-9\-]+)(, \[2\] = ([0-9\-]+))?(, \[3\] = ([0-9\-]+))?(, \[4\] = ([0-9\-]+))?(, \[5\] = ([0-9\-]+))?(, \[6\] = ([0-9\-]+))?'
                                    match = re.match(pattern, line)
                                    if match:
                                        cn = match.group(1)
                                        sp = match.group(2)
                                        ph = match.group(3)
                                        slot_name = match.group(5)
                                        item_ids = {1: int(match.group(6))}
                                        for i, g in enumerate([8, 10, 12, 14, 16], start=2):
                                            try:
                                                if match.group(g):
                                                    item_ids[i] = int(match.group(g))
                                            except:
                                                pass
                                        
                                        # 填充 maxed_data
                                        if cn not in self.maxed_data:
                                            self.maxed_data[cn] = {}
                                        if sp not in self.maxed_data[cn]:
                                            self.maxed_data[cn][sp] = {}
                                        if ph not in self.maxed_data[cn][sp]:
                                            self.maxed_data[cn][sp][ph] = {}
                                        self.maxed_data[cn][sp][ph][slot_name] = {
                                            "item_ids": item_ids,
                                            "enhs": {}
                                        }
            
            print(f"加载完成")
            print(f"职业列表: {list(self.classes.keys())}")
            print(f"阶段列表: {self.phases}")
            print(f"解析到的装备数据: {len(self.maxed_data)} 个职业")
            
            self.update_ui()
        except Exception as e:
            print(f"加载毕业装备数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 使用默认数据
            self.classes = self.default_classes
            self.phases = self.default_phases
            self.maxed_data = {}
            self.update_ui_with_defaults()
    
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
    
    def update_ui(self):
        """用解析到的真实数据更新UI"""
        # 更新职业（显示中文）
        class_list = list(self.classes.keys())
        chinese_class_list = [self.class_name_mapping.get(cls, cls) for cls in class_list]
        self.class_combo['values'] = chinese_class_list
        if chinese_class_list:
            self.class_var.set(chinese_class_list[0])
            # 更新专精（显示中文）
            first_class = class_list[0]
            specs = self.classes.get(first_class, [])
            chinese_specs = [self.spec_name_mapping.get(spec, spec) for spec in specs]
            self.spec_combo['values'] = chinese_specs
            if chinese_specs:
                self.spec_var.set(chinese_specs[0])
        # 更新阶段
        self.phase_combo['values'] = self.phases
        self.phase_var.set("P3" if "P3" in self.phases else (self.phases[0] if self.phases else "P3"))
        # 更新槽位（显示中文）
        chinese_slots = [self.slot_name_mapping.get(slot, slot) for slot in self.slots]
        self.slot_var.set(chinese_slots[0])
        # 更新当前装备ID显示
        self.update_current_items_display()
    
    def on_class_select(self, event=None):
        """选择职业后更新专精列表"""
        # 中文转英文职业名
        chinese_class = self.class_var.get()
        class_name = self.class_name_reverse.get(chinese_class, chinese_class)
        # 获取该职业的专精
        specs = self.classes.get(class_name, self.default_classes.get(class_name, []))
        # 专精显示中文
        chinese_specs = [self.spec_name_mapping.get(spec, spec) for spec in specs]
        print(f"更新专精列表: 职业={class_name}, 专精={specs}, 中文专精={chinese_specs}")
        self.spec_combo['values'] = chinese_specs
        if chinese_specs:
            self.spec_var.set(chinese_specs[0])
        # 更新装备显示
        self.update_current_items_display()
    
    def on_spec_select(self, event=None):
        """选择专精后更新装备显示"""
        print(f"选择专精: {self.spec_var.get()}")
        self.update_current_items_display()
    
    def on_phase_select(self, event=None):
        """选择阶段后更新装备显示"""
        print(f"选择阶段: {self.phase_var.get()}")
        self.update_current_items_display()
    
    def on_slot_select(self, event=None):
        """选择槽位后更新装备显示"""
        print(f"选择槽位: {self.slot_var.get()}")
        self.update_current_items_display()
    
    def update_current_items_display(self):
        """更新当前选中条件下的装备ID显示"""
        # 清空当前显示
        for i, label in enumerate(self.current_items_labels):
            label.config(text=f"{i+1}: -")
        
        # 获取选中条件
        chinese_class = self.class_var.get()
        chinese_spec = self.spec_var.get()
        phase = self.phase_var.get()
        chinese_slot = self.slot_var.get()
        
        # 中文转英文
        class_name = self.class_name_reverse.get(chinese_class, chinese_class)
        spec = self.spec_name_reverse.get(chinese_spec, chinese_spec)
        slot_name = self.slot_name_reverse.get(chinese_slot, chinese_slot)
        
        # 处理远程槽位的映射
        remote_slots = ["Relic", "Ranged", "Wand", "Totem", "Sigil", "Sanctified"]
        
        # 如果当前槽位是远程槽位，尝试匹配所有可能的远程槽位英文名称
        if slot_name == "Relic":
            # 先尝试使用原始槽位名称查找
            if class_name in self.maxed_data and spec in self.maxed_data[class_name] and phase in self.maxed_data[class_name][spec]:
                phase_data = self.maxed_data[class_name][spec][phase]
                # 检查是否有远程槽位的数据
                for remote_slot in remote_slots:
                    if remote_slot in phase_data:
                        slot_name = remote_slot
                        break
        
        print(f"更新装备显示: 职业={chinese_class}({class_name}), 专精={chinese_spec}({spec}), 阶段={phase}, 槽位={chinese_slot}({slot_name})")
        
        # 读取对应数据
        try:
            print(f"检查数据结构: 职业={class_name in self.maxed_data}, 专精={spec in self.maxed_data.get(class_name, {})}, 阶段={phase in self.maxed_data.get(class_name, {}).get(spec, {})}, 槽位={slot_name in self.maxed_data.get(class_name, {}).get(spec, {}).get(phase, {})}")
            
            if class_name in self.maxed_data and spec in self.maxed_data[class_name] and phase in self.maxed_data[class_name][spec] and slot_name in self.maxed_data[class_name][spec][phase]:
                slot_data = self.maxed_data[class_name][spec][phase][slot_name]
                item_ids = slot_data["item_ids"]
                print(f"找到装备ID: {item_ids}")
                # 更新显示
                for i in range(1,3):
                    self.current_items_labels[i-1].config(text=f"{i}: {item_ids.get(i, -1)}")
                # 保存当前装备ID列表
                self.current_items = [item_ids.get(i, -1) for i in range(1,3)]
                self.current_enhs = slot_data.get("enhs", {})
            else:
                # 无数据时初始化
                print("未找到对应数据")
                self.current_items = [-1]*2
                self.current_enhs = {}
        except Exception as e:
            print(f"更新装备显示失败: {str(e)}")
            # 无数据时初始化
            self.current_items = [-1]*2
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
            
            # 处理远程槽位的映射
            remote_slots = ["Relic", "Ranged", "Wand", "Totem", "Sigil", "Sanctified"]
            
            # 如果当前槽位是远程槽位，尝试匹配所有可能的远程槽位英文名称
            if slot_name == "Relic":
                # 先尝试使用原始槽位名称查找
                if class_name in self.maxed_data and spec in self.maxed_data[class_name] and phase in self.maxed_data[class_name][spec]:
                    phase_data = self.maxed_data[class_name][spec][phase]
                    # 检查是否有远程槽位的数据
                    for remote_slot in remote_slots:
                        if remote_slot in phase_data:
                            slot_name = remote_slot
                            break
            
            # 检查是否允许修改第二个位置
            if position == 2 and slot_name not in self.double_slots:
                messagebox.showwarning("警告", "只有戒指和饰品可以设置第二个位置")
                return
            
            # 确定目标文件路径
            spec_file = os.path.join(self.maxed_data_dir, class_name, f"{spec}.lua")
            print(f"目标文件路径: {spec_file}")
            print(f"文件是否存在: {os.path.exists(spec_file)}")
            
            if not os.path.exists(spec_file):
                messagebox.showerror("错误", f"数据文件不存在: {spec_file}")
                return
            
            print(f"查找条件: class={class_name}, spec={spec}, phase={phase}, slot={slot_name}, position={position}")
            
            # 读取文件内容
            with open(spec_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 查找并修改目标行
            new_lines = []
            found = False
            
            for line in lines:
                if 'TitanBistooltip_Maxed_bislists' in line:
                    print(f"检查行: {line[:80]}...")
                    print(f"  匹配class: {f'[\"{class_name}\"]' in line}")
                    print(f"  匹配spec: {f'[\"{spec}\"]' in line}")
                    print(f"  匹配phase: {f'[\"{phase}\"]' in line}")
                    print(f"  匹配slot: {f'[\"slot_name\"] = \"{slot_name}\"' in line}")
                if 'TitanBistooltip_Maxed_bislists' in line and f'["{class_name}"]' in line and f'["{spec}"]' in line and f'["{phase}"]' in line:
                    if f'["slot_name"] = "{slot_name}"' in line:
                        # 找到目标行，修改指定位置的装备ID
                        idx = line.rfind(f'[{position}] = ')
                        if idx != -1:
                            num_start = idx + len(f'[{position}] = ')
                            # 找到数字后面的结束位置
                            end_pos = -1
                            for i in range(num_start, len(line)):
                                if line[i] in ',}':
                                    end_pos = i
                                    break
                            if end_pos != -1:
                                new_line = line[:num_start] + f'{item_id}' + line[end_pos:]
                                new_lines.append(new_line)
                                found = True
                                print(f"更新行: {line.strip()} -> {new_line.strip()}")
                            else:
                                new_lines.append(line)
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            if not found:
                messagebox.showerror("错误", f"未找到{chinese_class}-{chinese_spec}-{phase}-{chinese_slot}的配置行")
                return
            
            # 写入文件
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            # 更新内存数据
            if class_name in self.maxed_data and spec in self.maxed_data[class_name] and phase in self.maxed_data[class_name][spec] and slot_name in self.maxed_data[class_name][spec][phase]:
                self.maxed_data[class_name][spec][phase][slot_name]["item_ids"][position] = item_id
            
            # 更新 UI 显示
            self.update_current_items_display()
            
            # 显示成功消息
            messagebox.showinfo("成功", f"已保存：{chinese_class}-{chinese_spec}-{phase}-{chinese_slot} 位置{position} → {item_id}")
            self.status_var.set("保存成功")
        except Exception as e:
            print(f"保存失败：{str(e)}")
            messagebox.showerror("错误", f"保存失败：{str(e)}")
            self.status_var.set("保存失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = MaxedDatabaseUpdater(root)
    root.mainloop()