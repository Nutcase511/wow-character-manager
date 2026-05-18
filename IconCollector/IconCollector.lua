-- IconCollector - 装备图标收集插件 (Wrath 3.3.5/泰坦重铸兼容版)
local addonName, addonNS = ...

local ZG_ITEM_IDS = {
    19716, 19717, 19718, 19719, 19720, 19721, 19722, 19723, 19724, 19802,
    19852, 19853, 19854, 19855, 19856, 19857, 19859, 19861, 19862, 19863,
    19864, 19865, 19866, 19867, 19869, 19870, 19871, 19872, 19873, 19874,
    19875, 19876, 19877, 19878, 19884, 19885, 19886, 19887, 19888, 19889,
    19890, 19891, 19892, 19893, 19894, 19895, 19896, 19897, 19898, 19899,
    19900, 19901, 19902, 19903, 19904, 19905, 19906, 19907, 19909, 19910,
    19912, 19913, 19914, 19915, 19918, 19919, 19920, 19922, 19923, 19925,
    19927, 19928, 19929, 19930, 19939, 19940, 19941, 19942, 19944, 19945,
    19946, 19947, 19961, 19962, 19963, 19964, 19965, 19967, 19968, 19993,
    20032, 20038, 20260, 20262, 20265, 20266, 22637, 22739,
}

local function extractIconName(texturePath)
    if not texturePath then return nil end
    local name = string.match(texturePath, "Interface\\Icons\\(.+)")
    if not name then name = string.match(texturePath, "(.+)") end
    return name
end

local function scanItem(itemId)
    local _, itemName, _, _, _, _, _, _, _, texture = GetItemInfo(itemId)
    if itemName then
        local iconName = extractIconName(texture)
        return itemName, iconName
    end
    return nil, nil
end

local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:SetScript("OnEvent", function(self, event, arg1)
    if event == "ADDON_LOADED" and arg1 == addonName then
        if not IconCollectorDB then IconCollectorDB = {} end
        if not IconCollectorDB.raid then IconCollectorDB.raid = {} end
        print("|cff00ff00IconCollector 加载成功!|r")
        print("  /ic raid - 扫描60/70级团本装备图标(" .. #RAID_ITEM_IDS .. "个)")
        print("  /ic zgloot - 扫描祖尔格拉布装备图标(" .. #ZG_ITEM_IDS .. "个)")
        print("  /ic info - 查看进度")
        print("输入 /ic export 导出数据")
    end
end)

SLASH_IC1, SLASH_IC2, SLASH_IC3 = "/ic", "/iconcollector", "/ic"

SlashCmdList["IC"] = function(msg)
    msg = string.lower(msg or "")
    msg = string.gsub(msg, "^%s+", "")
    msg = string.gsub(msg, "%s+$", "")
    local parts = {}
    for word in string.gmatch(msg, "%S+") do
        table.insert(parts, word)
    end

    if #parts == 0 then
        print("使用说明:")
        print("  /ic raid - 扫描60/70级团本装备图标(" .. #RAID_ITEM_IDS .. "个)")
        print("  /ic zgloot - 扫描祖尔格拉布装备图标(" .. #ZG_ITEM_IDS .. "个)")
        print("  /ic info - 查看扫描进度")
        print("  /ic export - 导出图标映射表")
        print("  /ic reset - 清空扫描结果重新扫描")

    elseif parts[1] == "raid" then
        local db = IconCollectorDB.raid
        local queue = {}
        for _, itemId in ipairs(RAID_ITEM_IDS) do
            if not db[tostring(itemId)] then
                table.insert(queue, itemId)
            end
        end

        if #queue == 0 then
            print("所有物品已扫描完成! 输入 /ic info 查看结果")
            return
        end

        local total = #queue

        print("开始扫描 " .. total .. " 个物品...")
        print("扫描中，请稍候...")

        local scanFrame = CreateFrame("Frame")
        local idx = 1
        local found = 0
        scanFrame:SetScript("OnUpdate", function(self, elapsed)
            self.elapsed = (self.elapsed or 0) + elapsed
            if self.elapsed >= 0.02 then
                self.elapsed = 0
                if idx <= total then
                    local itemId = queue[idx]
                    local itemName, iconName = scanItem(itemId)
                    if itemName then
                        db[tostring(itemId)] = { name = itemName, icon = iconName }
                        found = found + 1
                    end
                    if found > 0 and found % 100 == 0 then
                        print("已扫描 " .. idx .. "/" .. total .. ", 找到 " .. found .. " 个")
                    end
                    idx = idx + 1
                else
                    print("扫描完成! 共扫描" .. total .. "个物品, " .. found .. "个找到图标")
                    self:SetScript("OnUpdate", nil)
                end
            end
        end)

    elseif parts[1] == "zgloot" then
        local db = IconCollectorDB.raid
        local queue = {}
        for _, itemId in ipairs(ZG_ITEM_IDS) do
            if not db[tostring(itemId)] then
                table.insert(queue, itemId)
            end
        end

        if #queue == 0 then
            print("祖尔格拉布物品已扫描完成!")
            return
        end

        print("开始扫描 " .. #queue .. " 个祖尔格拉布物品...")
        local scanFrame = CreateFrame("Frame")
        local idx = 1
        local found = 0
        scanFrame:SetScript("OnUpdate", function(self, elapsed)
            self.elapsed = (self.elapsed or 0) + elapsed
            if self.elapsed >= 0.02 then
                self.elapsed = 0
                if idx <= #queue then
                    local itemId = queue[idx]
                    local itemName, iconName = scanItem(itemId)
                    if itemName then
                        db[tostring(itemId)] = { name = itemName, icon = iconName }
                        found = found + 1
                    end
                    if found > 0 and found % 30 == 0 then
                        print("已扫描 " .. idx .. "/" .. #queue .. ", 找到 " .. found .. " 个")
                    end
                    idx = idx + 1
                else
                    print("扫描完成! 祖尔格拉布物品找到 " .. found .. " 个图标")
                    self:SetScript("OnUpdate", nil)
                end
            end
        end)

    elseif parts[1] == "info" then
        local db = IconCollectorDB.raid
        local count = 0
        for _ in pairs(db) do
            count = count + 1
        end
        print("已收集 " .. count .. "/" .. #RAID_ITEM_IDS .. " 个图标")
        if count > 0 then
            print("输入 /ic export 导出数据")
        end

    elseif parts[1] == "export" then
        local db = IconCollectorDB.raid
        local count = 0
        for _ in pairs(db) do count = count + 1 end
        if count == 0 then
            print("没有扫描数据，请先输入 /ic raid")
            return
        end
        print("已将 " .. count .. " 个物品写入存档文件")
        print("请执行 /reloadui 将数据保存到磁盘")
        print("然后运行: python IconCollector/import_icons.py")

    elseif parts[1] == "reset" then
        IconCollectorDB.raid = {}
        print("已清空扫描结果，输入 /ic raid 重新扫描")
    end
end