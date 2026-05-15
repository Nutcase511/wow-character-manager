local LibExtraTip = LibStub:GetLibrary("LibExtraTip-1");
local eventFrame = CreateFrame("Frame", nil, UIParent)
local L = LibStub("AceLocale-3.0"):GetLocale("TitanBistooltip", false)
TitanBistooltip_phases_string = ""
TitanBistooltip_Titan_items = {}

-- 确保全局变量存在
Maxed = Maxed or {}
InterfaceOptionsFrame = InterfaceOptionsFrame or nil
AceConfigDialog = AceConfigDialog or LibStub("AceConfigDialog-3.0", true)

-- 快捷键绑定定义
BINDING_HEADER_TITANBISTOOLTIP = "TitanBistooltip"
BINDING_NAME_TOGGLE_BISLIST = L["打开/关闭 BIS面板"] or "Toggle BIS Panel"
BINDING_NAME_TOGGLE_MAXED = L["打开/关闭 毕业配装面板"] or "Toggle Maxed Panel"

local function specHighlighted(class_name, spec_name)
    -- 遍历所有职业，检查当前职业是否在高亮列表中
    for key, value in pairs(TitanBistooltipAddon.db.global.highlight_specs) do
        if value then
            local ci, si = strsplit(":", key)
            ci = tonumber(ci)
            si = tonumber(si)
            if ci and si and TitanBistooltip_classes[ci] then
                local highlight_class_name = TitanBistooltip_classes[ci].name
                local highlight_spec_name = TitanBistooltip_classes[ci].specs[si]
                if highlight_class_name == class_name and highlight_spec_name == spec_name then
                    return true
                end
            end
        end
    end
    return false
end

local function specFiltered(class_name, spec_name)
    if specHighlighted(class_name, spec_name) then
        return false
    end
    if IsAltKeyDown() then
        return false
    end
    
    -- 处理术士的Destruction fire映射到Destruction
    local actual_spec_name = spec_name
    if class_name == "Warlock" and spec_name == "Destruction fire" then
        actual_spec_name = "Destruction"
    end
    
    -- 确保过滤配置存在且默认值为false
    if not TitanBistooltipAddon.db.global.filter_specs[class_name] then
        TitanBistooltipAddon.db.global.filter_specs[class_name] = {}
    end
    if TitanBistooltipAddon.db.global.filter_specs[class_name][actual_spec_name] == nil then
        TitanBistooltipAddon.db.global.filter_specs[class_name][actual_spec_name] = false
    end
    
    return TitanBistooltipAddon.db.global.filter_specs[class_name][actual_spec_name]
end

local function classNamesFiltered()
    if TitanBistooltipAddon.db.global.filter_class_names then
        return true
    end
end

local function getFilteredItem(item)
    local filtered_item = {}

    for ki, spec in ipairs(item) do
        local class_name = spec.class_name
        local spec_name = spec.spec_name
        
        if (not specFiltered(class_name, spec_name)) then
            table.insert(filtered_item, spec)
        end
    end
    
    return filtered_item
end

-- 缓存排名数据，避免重复计算
local rank_cache = {}

local function getDynamicRank(itemId, class_name, spec_name, slot_name)
    -- 生成缓存键，包含过滤配置
    local filter_key = ""
    if TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.filter_phases then
        for _, phase in ipairs(TitanBistooltip_phases or {}) do
            filter_key = filter_key .. (TitanBistooltipAddon.db.global.filter_phases[phase] and "1" or "0")
        end
    end
    
    -- 添加隐藏传说装备配置到缓存键
    local hideLegendary = TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.hide_legendary_items == true
    filter_key = filter_key .. (hideLegendary and "1" or "0")
    
    local cache_key = itemId .. "|" .. class_name .. "|" .. spec_name .. "|" .. slot_name .. "|" .. filter_key
    
    -- 检查缓存是否存在
    if rank_cache[cache_key] then
        return rank_cache[cache_key]
    end
    
    -- 根据 TitanBistooltip_bislists 中的数据动态计算排名
    local phases = TitanBistooltip_phases or {}
    local dynamic_ranks = {}
    local has_rank = false
    
    for phase_index, phase_name in ipairs(phases) do
        -- 检查该阶段是否被过滤
        if not (TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.filter_phases and TitanBistooltipAddon.db.global.filter_phases[phase_name]) then
            local phase_rank = "-"
            
            -- 检查该阶段是否有数据
            if TitanBistooltip_bislists and 
               TitanBistooltip_bislists[class_name] and 
               TitanBistooltip_bislists[class_name][spec_name] and 
               TitanBistooltip_bislists[class_name][spec_name][phase_name] then
                
                -- 遍历该阶段的装备槽
                local slots = TitanBistooltip_bislists[class_name][spec_name][phase_name]
                if slots then
                    for _, slot in ipairs(slots) do
                        if slot and slot.slot_name == slot_name then
                            -- 计算有效排名（过滤传说装备）
                            local effective_rank = 0
                            for rank = 1, 6 do
                                if slot[rank] and slot[rank] ~= -1 then
                                    -- 如果启用了隐藏传说装备选项，检查当前装备是否是传说装备
                                    local shouldCount = true
                                    if hideLegendary and TitanBistooltip_legendary_names then
                                        -- 获取装备名称
                                        local itemName = GetItemInfo(slot[rank])
                                        if itemName and TitanBistooltip_legendary_names[itemName] then
                                            shouldCount = false
                                        end
                                    end
                                    
                                    if shouldCount then
                                        effective_rank = effective_rank + 1
                                        if slot[rank] == itemId then
                                            phase_rank = tostring(effective_rank)
                                            has_rank = true
                                        end
                                    end
                                end
                            end
                        end
                    end
                end
            end
            
            table.insert(dynamic_ranks, phase_rank)
        end
    end
    
    -- 如果装备在所有可见阶段中都没有排名，返回空表
    if not has_rank then
        dynamic_ranks = {}
    end
    
    -- 缓存结果
    rank_cache[cache_key] = dynamic_ranks
    
    -- 返回排名表，而不是拼接后的字符串，以便后续处理对齐
    return dynamic_ranks
end

local currentItemId = nil

-- 缓存格式化的排名字符串
local formatted_ranks_cache = {}

local function printSpecLine(tooltip, slot, class_name, spec_name)
    local slot_name = slot.name
    local prefix = "   "
    if TitanBistooltipAddon.db.global.filter_class_names then
        prefix = ""
    end
    local left_text = prefix
    -- 检查TitanBistooltip_spec_icons是否存在
    if TitanBistooltip_spec_icons and TitanBistooltip_spec_icons[class_name] and TitanBistooltip_spec_icons[class_name][spec_name] then
        left_text = left_text .. "|T" .. TitanBistooltip_spec_icons[class_name][spec_name] .. ":14|t "
    end
    left_text = left_text .. L[spec_name]
    if (slot_name == "Off hand" or slot_name == "Weapon" or slot_name == "Weapon 1h" or slot_name == "Weapon 2h") then
        left_text = left_text .. " (" .. L[slot_name] .. ")"
    end
    local color_r = 1
    local color_g = 0.8
    local color_b = 0
    if specHighlighted(class_name, spec_name) then
        color_r = 0.074
        color_g = 0.964
        color_b = 0.129
    end
    
    -- 生成缓存键，包含过滤配置
    local filter_key = ""
    if TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.filter_phases then
        for _, phase in ipairs(TitanBistooltip_phases or {}) do
            filter_key = filter_key .. (TitanBistooltipAddon.db.global.filter_phases[phase] and "1" or "0")
        end
    end
    local cache_key = currentItemId .. "|" .. class_name .. "|" .. spec_name .. "|" .. slot_name .. "|" .. filter_key
    
    -- 检查缓存是否存在
    local formatted_ranks = formatted_ranks_cache[cache_key]
    if not formatted_ranks then
        -- 动态计算排名
        local slot_ranks = getDynamicRank(currentItemId, class_name, spec_name, slot_name)
        
        -- ==============================================
        -- 【核心修改】只显示有排名的阶段
        -- ==============================================
        if type(slot_ranks) == "table" then
            -- 只保留有排名的阶段
            local parts = {}
            for _, rank in ipairs(slot_ranks) do
                if rank ~= "-" then
                    table.insert(parts, rank)
                end
            end
            
            -- 如果所有阶段都没有排名，显示"-"
            if #parts == 0 then
                formatted_ranks = "-"
            else
                -- 用 "-" 连接
                formatted_ranks = table.concat(parts, "-")
            end
        else
            formatted_ranks = slot_ranks or "-"
        end
        
        -- 缓存结果
        formatted_ranks_cache[cache_key] = formatted_ranks
    end
    
    LibExtraTip:AddDoubleLine(
            tooltip, left_text, formatted_ranks,
            color_r, color_g, color_b,
            color_r, color_g, color_b,
            false) -- 设置为false，使用默认对齐方式
end

local function printClassName(tooltip, class_name)
    LibExtraTip:AddLine(tooltip, L[class_name], 1, 0.8, 0, false)
end

local function OnGameTooltipSetItem(tooltip)
    -- 检查是否禁用了鼠标BIS增强提示
    if TitanBistooltipAddon.db.global.disable_tooltip_enhancement then
        return
    end
    
    if TitanBistooltipAddon.db.global.tooltip_with_ctrl and not IsControlKeyDown() then
        return
    end
    local _, link = tooltip:GetItem();

    if link == nil then
        return ;
    end
    


    local _, itemId, _, _, _, _, _, _, _, _, _, _, _, _ = strsplit(":", link)

    if not itemId then
        return;
    end

    itemId = tonumber(itemId);
    if not itemId then
        return;
    end
    currentItemId = itemId; -- 保存到全局变量
    
    -- 使用装备映射表快速获取装备信息
    local dynamic_item_data = {}
    local found = false
    
    -- 无论是否在战斗中，都从映射表或BIS列表中获取数据
    -- 检查装备是否在映射表中
    if TitanBistooltip_item_mapping and TitanBistooltip_item_mapping[itemId] then
        -- 从映射表中获取装备信息
        for combo_key, _ in pairs(TitanBistooltip_item_mapping[itemId]) do
            local class_name, spec_name, slot_name = strsplit("|", combo_key)
            table.insert(dynamic_item_data, {
                class_name = class_name,
                spec_name = spec_name,
                slot_name = slot_name
            })
            found = true
        end
        
        -- 同时更新TitanBistooltip_Titan_items缓存（如果不存在）
        if not TitanBistooltip_Titan_items[itemId] then
            TitanBistooltip_Titan_items[itemId] = {}
            
            -- 添加缓存时间戳
            TitanBistooltip_Titan_items[itemId]._cache_time = GetTime()
            
            -- 按职业分组，同一职业的所有专精都放在一起
            local class_map = {}
            for _, entry in ipairs(dynamic_item_data) do
                local class_name = entry.class_name
                local spec_name = entry.spec_name
                local slot_name = entry.slot_name
                
                -- 检查职业是否已经存在
                if not class_map[class_name] then
                    class_map[class_name] = {}
                end
                
                -- 检查专精是否已经存在
                if not class_map[class_name][spec_name] then
                    class_map[class_name][spec_name] = {
                        class_name = class_name,
                        spec_name = spec_name,
                        slots = {}
                    }
                end
                
                -- 检查槽位是否已经存在
                local slot_exists = false
                for _, existing_slot in ipairs(class_map[class_name][spec_name].slots) do
                    if existing_slot.name == slot_name then
                        slot_exists = true
                        break
                    end
                end
                
                if not slot_exists then
                    -- 添加槽位
                    table.insert(class_map[class_name][spec_name].slots, {
                        name = slot_name,
                        ranks = "- / - / -" -- 占位符，实际排名会动态计算
                    })
                end
            end
            
            -- 转换为TitanBistooltip_Titan_items的格式
            for _, specs in pairs(class_map) do
                for _, item_info in pairs(specs) do
                    table.insert(TitanBistooltip_Titan_items[itemId], item_info)
                end
            end
        end
    else
        -- 回退到传统方法（如果映射表中没有）
        local temp_item_data = {}
        
        if TitanBistooltip_bislists then
            for class_name, class_data in pairs(TitanBistooltip_bislists) do
                for spec_name, spec_data in pairs(class_data) do
                    for phase_name, phase_data in pairs(spec_data) do
                        for _, slot_data in ipairs(phase_data) do
                            for i = 1, 6 do
                                if slot_data[i] == itemId then
                                    -- 找到装备在BIS列表中的位置
                                    local slot_name = slot_data.slot_name
                                    
                                    -- 检查是否已经添加过相同的职业-专精-槽位组合
                                    local already_exists = false
                                    for _, entry in ipairs(temp_item_data) do
                                        if entry.class_name == class_name and entry.spec_name == spec_name and entry.slot_name == slot_name then
                                            already_exists = true
                                            break
                                        end
                                    end
                                    
                                    if not already_exists then
                                        -- 添加到动态装备数据中
                                        table.insert(temp_item_data, {
                                            class_name = class_name,
                                            spec_name = spec_name,
                                            slot_name = slot_name
                                        })
                                        found = true
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
        
        if found then
            dynamic_item_data = temp_item_data
            
            -- 更新缓存
            TitanBistooltip_Titan_items[itemId] = {}
            TitanBistooltip_Titan_items[itemId]._cache_time = GetTime()
            
            local class_map = {}
            for _, entry in ipairs(temp_item_data) do
                local class_name = entry.class_name
                local spec_name = entry.spec_name
                local slot_name = entry.slot_name
                
                if not class_map[class_name] then
                    class_map[class_name] = {}
                end
                
                if not class_map[class_name][spec_name] then
                    class_map[class_name][spec_name] = {
                        class_name = class_name,
                        spec_name = spec_name,
                        slots = {}
                    }
                end
                
                local slot_exists = false
                for _, existing_slot in ipairs(class_map[class_name][spec_name].slots) do
                    if existing_slot.name == slot_name then
                        slot_exists = true
                        break
                    end
                end
                
                if not slot_exists then
                    table.insert(class_map[class_name][spec_name].slots, {
                        name = slot_name,
                        ranks = "- / - / -"
                    })
                end
            end
            
            for _, specs in pairs(class_map) do
                for _, item_info in pairs(specs) do
                    table.insert(TitanBistooltip_Titan_items[itemId], item_info)
                end
            end
        end
    end
    
    -- 如果没有找到装备信息，尝试从缓存中获取数据
    if not found and TitanBistooltip_Titan_items[itemId] then
        -- 检查装备是否真的在BIS列表中
        local actually_exists = false
        if TitanBistooltip_bislists then
            for class_name, class_data in pairs(TitanBistooltip_bislists) do
                for spec_name, spec_data in pairs(class_data) do
                    for phase_name, phase_data in pairs(spec_data) do
                        for _, slot_data in ipairs(phase_data) do
                            for i = 1, 6 do
                                if slot_data[i] == itemId then
                                    actually_exists = true
                                    break
                                end
                            end
                            if actually_exists then
                                break
                            end
                        end
                        if actually_exists then
                            break
                        end
                    end
                    if actually_exists then
                        break
                    end
                end
                if actually_exists then
                    break
                end
            end
        end
        
        -- 只有当装备真的在BIS列表中时，才从缓存中读取数据
        if actually_exists then
            for _, item_info in pairs(TitanBistooltip_Titan_items[itemId]) do
                -- 跳过缓存时间字段
                if type(item_info) == "table" and item_info.class_name then
                    local class_name = item_info.class_name
                    local spec_name = item_info.spec_name
                    for _, slot_info in pairs(item_info.slots) do
                        local slot_name = slot_info.name
                        table.insert(dynamic_item_data, {
                            class_name = class_name,
                            spec_name = spec_name,
                            slot_name = slot_name
                        })
                    end
                end
            end
            found = #dynamic_item_data > 0
        end
    end
    
    -- 如果没有找到装备信息，直接返回
    if not found then
        return
    end
    
    -- 计算在没有用户专精过滤的情况下，所有相关专精的数据（用于比较）
    local function getAllSpecsWithoutUserFilter(item_list)
        local result = {}
        for _, spec in ipairs(item_list) do
            local class_name = spec.class_name
            local spec_name = spec.spec_name
            
            -- 临时检查该专精是否被用户过滤（不考虑ALT键）
            local is_filtered_by_user = false
            if TitanBistooltipAddon.db.global.filter_specs[class_name] then
                -- 处理术士的Destruction fire映射到Destruction
                local actual_spec_name = spec_name
                if class_name == "Warlock" and spec_name == "Destruction fire" then
                    actual_spec_name = "Destruction"
                end
                is_filtered_by_user = TitanBistooltipAddon.db.global.filter_specs[class_name][actual_spec_name] == true
            end
            
            if not is_filtered_by_user then
                table.insert(result, spec)
            end
        end
        return result
    end
    
    -- 没有用户专精过滤时的数据
    local all_data_without_user_filter = getAllSpecsWithoutUserFilter(dynamic_item_data)
    
    -- 应用过滤，根据用户设置显示相关专精
    local filtered_item_data = getFilteredItem(dynamic_item_data)
    
    -- 过滤掉在所有可见阶段中都没有排名的专精
    local final_filtered_item_data = {}
    for _, spec in ipairs(filtered_item_data) do
        local slot_ranks = getDynamicRank(currentItemId, spec.class_name, spec.spec_name, spec.slot_name)
        if type(slot_ranks) == "table" and #slot_ranks > 0 then
            table.insert(final_filtered_item_data, spec)
        end
    end
    
    -- 对没有用户专精过滤的数据也应用阶段排名过滤
    local final_all_data_without_user_filter = {}
    for _, spec in ipairs(all_data_without_user_filter) do
        local slot_ranks = getDynamicRank(currentItemId, spec.class_name, spec.spec_name, spec.slot_name)
        if type(slot_ranks) == "table" and #slot_ranks > 0 then
            table.insert(final_all_data_without_user_filter, spec)
        end
    end
    
    if (#final_filtered_item_data > 0) then
        -- 检查是否有可见阶段
        local has_visible_phases = false
        local visible_phases = {}
        for _, phase in ipairs(TitanBistooltip_phases or {}) do
            if not (TitanBistooltipAddon.db and TitanBistooltipAddon.db.global and TitanBistooltipAddon.db.global.filter_phases and TitanBistooltipAddon.db.global.filter_phases[phase]) then
                has_visible_phases = true
                table.insert(visible_phases, phase)
            end
        end
        
        if has_visible_phases then
            -- 收集所有有排名的阶段
            local phases_with_rank = {}
            for _, spec in ipairs(final_filtered_item_data) do
                local slot_ranks = getDynamicRank(currentItemId, spec.class_name, spec.spec_name, spec.slot_name)
                if type(slot_ranks) == "table" then
                    for i, rank in ipairs(slot_ranks) do
                        if rank ~= "-" and i <= #visible_phases then
                            local phase = visible_phases[i]
                            local found = false
                            for _, p in ipairs(phases_with_rank) do
                                if p == phase then
                                    found = true
                                    break
                                end
                            end
                            if not found then
                                table.insert(phases_with_rank, phase)
                            end
                        end
                    end
                end
            end
            
            -- 如果有阶段有排名，显示阶段标题
            if #phases_with_rank > 0 then
                local current_phases_string = ""
                local fixed_order = {"PR","P1","P2","P3","P4","P5","P6","P7","P8","P9","P10","P11"}
                for _, p in ipairs(fixed_order) do
                    for _, phase in ipairs(phases_with_rank) do
                        if phase == p then
                            current_phases_string = current_phases_string .. p
                            break
                        end
                    end
                end
                LibExtraTip:AddDoubleLine(tooltip, L["Spec name"], current_phases_string, 1, 1, 0, 1, 1, 0, false)
            end
        end
    else
        return
    end
    
    -- 更新过滤后的数据
    filtered_item_data = final_filtered_item_data
    
    -- 按职业排序，当前角色的职业显示在最上面，其他职业保持固定排序
    local player_class_en
    if C_PlayerInfo and C_PlayerInfo.GetClass then
        local classInfo
        -- 尝试使用 PlayerLocation 对象（现代API）
        if PlayerLocation and PlayerLocation.CreateFromUnit then
            local playerLocation = PlayerLocation:CreateFromUnit("player")
            classInfo = C_PlayerInfo.GetClass(playerLocation)
        end
        -- 如果现代API失败，尝试使用字符串 "player"（旧API）
        if not classInfo then
            classInfo = C_PlayerInfo.GetClass("player")
        end
        if classInfo then
            player_class_en = classInfo.classFile
        end
    else
        local _, player_class_en_temp = UnitClass("player")
        player_class_en = player_class_en_temp
    end
    -- 职业名称映射表，将游戏返回的英文职业名映射到数据库中使用的格式
    local class_name_mapping = {
        ["DEATHKNIGHT"] = "Death knight",
        ["DRUID"] = "Druid",
        ["HUNTER"] = "Hunter",
        ["MAGE"] = "Mage",
        ["PALADIN"] = "Paladin",
        ["PRIEST"] = "Priest",
        ["ROGUE"] = "Rogue",
        ["SHAMAN"] = "Shaman",
        ["WARRIOR"] = "Warrior",
        ["WARLOCK"] = "Warlock"
    }
    local player_class
    if player_class_en then
        player_class = class_name_mapping[string.upper(player_class_en)] or player_class_en
    end
    
    local class_order = {
        ["Death knight"] = 1,
        ["Druid"] = 2,
        ["Hunter"] = 3,
        ["Mage"] = 4,
        ["Paladin"] = 5,
        ["Priest"] = 6,
        ["Rogue"] = 7,
        ["Shaman"] = 8,
        ["Warrior"] = 9,
        ["Warlock"] = 10
    }
    
    table.sort(filtered_item_data, function(a, b)
        -- 当前角色的职业排在最前面
        if a.class_name == player_class and b.class_name ~= player_class then
            return true
        elseif a.class_name ~= player_class and b.class_name == player_class then
            return false
        end
        -- 其他职业按照固定顺序排序
        local order_a = class_order[a.class_name] or 999
        local order_b = class_order[b.class_name] or 999
        if order_a ~= order_b then
            return order_a < order_b
        end
        -- 同一职业的专精按名称排序
        return a.spec_name < b.spec_name
    end)
    
    local previous_class = nil
    for ki, spec in ipairs(filtered_item_data) do
        local class_name = spec.class_name
        local spec_name = spec.spec_name
        local slot_name = spec.slot_name
        
        if (not classNamesFiltered()) then
            if not (previous_class == class_name) then
                printClassName(tooltip, class_name)
                previous_class = class_name
            end
        end
        
        -- 创建临时slot对象用于printSpecLine函数
        local temp_slot = {
            name = slot_name
        }
        
        -- 检查该专精在可见阶段中是否有排名
        local slot_ranks = getDynamicRank(currentItemId, class_name, spec_name, slot_name)
        if type(slot_ranks) == "table" and #slot_ranks > 0 then
            printSpecLine(tooltip, temp_slot, class_name, spec_name)
        end
    end
    if #filtered_item_data > 0 and TitanBistooltip_char_equipment and TitanBistooltip_char_equipment[itemId] ~= nil then
        LibExtraTip:AddLine(tooltip, " ", 1, 1, 0, false)
        if TitanBistooltip_char_equipment[itemId] == 2 then
            LibExtraTip:AddLine(tooltip, L["You have this item equipped"], 0.074, 0.964, 0.129, false)
        else
            LibExtraTip:AddLine(tooltip, L["You have this item"], 0.074, 0.964, 0.129, false)
        end
    end
    -- 只有当有专精被用户显式过滤时才显示提示（不包括阶段排名过滤）
    if #final_filtered_item_data < #final_all_data_without_user_filter then
        if #filtered_item_data > 0 then
            LibExtraTip:AddLine(tooltip, " ", 1, 1, 0, false)
        end
        LibExtraTip:AddLine(tooltip, L["Hold ALT to disable spec filtering"], 0.6, 0.6, 0.6, false)
    end
end

function TitanBistooltipAddon:initBisTooltip()
    -- 检测 TipTac 及其相关插件是否存在
    local hasTipTac = false
    if IsAddOnLoaded then
        hasTipTac = IsAddOnLoaded("TipTac") or IsAddOnLoaded("TipTacItemRef") or IsAddOnLoaded("TipTacTalents")
    end
    TitanBistooltipAddon.hasTipTac = hasTipTac
    
    -- 检查是否禁用了鼠标BIS增强提示
    if not TitanBistooltipAddon.db.global.disable_tooltip_enhancement and LibExtraTip then
        -- 只有在未禁用且LibExtraTip存在时才注册回调
        LibExtraTip:AddCallback({ type = "item", callback = OnGameTooltipSetItem, allevents = true })
        LibExtraTip:RegisterTooltip(GameTooltip);
        LibExtraTip:RegisterTooltip(ItemRefTooltip);
    end
    
    -- ESC键监听：关闭所有面板
    local escFrame = CreateFrame("Frame")
    escFrame:SetScript("OnKeyDown", function(self, key)
        if key == "ESCAPE" then
            TitanBistooltipAddon:closeAllPanels()
        end
    end)
    escFrame:SetPropagateKeyboardInput(true)
    TitanBistooltipAddon.escFrame = escFrame
    
    eventFrame:RegisterEvent("MODIFIER_STATE_CHANGED");
    eventFrame:SetScript("OnEvent", function(_, _, e_key, _, _)
        -- 如果 TipTac 存在，减少事件处理频率
        if hasTipTac then
            return
        end
        
        if (GameTooltip:GetOwner()) then
            if (GameTooltip:GetOwner().hasItem) then
                return
            end

            if (e_key == "RALT" or e_key == "LALT") then
                local _, link = GameTooltip:GetItem()
                if link then
                    GameTooltip:SetHyperlink("|cff9d9d9d|Hitem:3299::::::::20:257::::::|h[Fractured Canine]|h|r")
                    GameTooltip:SetHyperlink(link)
                end
            end
        end
    end)
end

function TitanBistooltipAddon:reinitBisTooltip()
    -- 配置已经保存，下次加载插件时会自动生效
    -- 不需要在这里做任何操作
end

function TitanBistooltipAddon:closeAllPanels()
    -- 关闭BIS面板
    if TitanBistooltipAddon.closeMainFrame then
        TitanBistooltipAddon:closeMainFrame()
    end
    
    -- 关闭毕业装面板
    if Maxed and Maxed.CloseFrame then
        Maxed:CloseFrame()
    end
    
    -- 关闭设置界面
    if InterfaceOptionsFrame then
        InterfaceOptionsFrame:Hide()
    end
    if AceConfigDialog and AceConfigDialog.CloseAll then
        AceConfigDialog:CloseAll()
    end
end
