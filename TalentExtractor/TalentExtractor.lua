local addonName, addonNS = ...
local frame = CreateFrame("Frame")

local CLASS_FILE_MAP = {
    ["WARRIOR"] = "warrior",
    ["PALADIN"] = "paladin",
    ["HUNTER"] = "hunter",
    ["ROGUE"] = "rogue",
    ["PRIEST"] = "priest",
    ["DEATHKNIGHT"] = "deathknight",
    ["SHAMAN"] = "shaman",
    ["MAGE"] = "mage",
    ["WARLOCK"] = "warlock",
    ["DRUID"] = "druid",
}

local function extractIconName(texturePath)
    if not texturePath then return nil end
    local name = string.match(texturePath, "Interface\\Icons\\(.+)")
    if not name then name = string.match(texturePath, "(.+)") end
    if name then name = string.gsub(name, "%.blp$", "") end
    return name
end

local function scanCurrentClass()
    local playerClass, classFile = UnitClass("player")
    if not playerClass then
        print("|cffff0000[TE] 错误: 无法获取职业信息")
        return false
    end

    classFile = classFile and classFile:upper() or ""
    local englishClass = CLASS_FILE_MAP[classFile]
    if not englishClass then
        print("|cffff0000[TE] 错误: 未知职业 " .. tostring(classFile))
        return false
    end

    local numTabs = GetNumTalentTabs()
    if not numTabs or numTabs == 0 then
        print("|cffff0000[TE] 错误: 需要至少10级才能查看天赋数据")
        return false
    end

    local data = {
        classFile = englishClass,
        className = playerClass,
        tabs = {}
    }

    for tabIdx = 1, numTabs do
        local tabName, tabIcon, pointsSpent, tabBg = GetTalentTabInfo(tabIdx)
        local numTalents = GetNumTalents(tabIdx)

        local tab = {
            name = tabName,
            icon = extractIconName(tabIcon),
            background = tabBg,
            nodes = {}
        }

        for talentIdx = 1, numTalents do
            local tName, tIcon, tier, column, currentRank, maxRank = GetTalentInfo(tabIdx, talentIdx)

            local description = ""
            local spellID = nil

            local ok, result = pcall(GetTalentSpellID, talentIdx, 1)
            if ok and result then
                spellID = result
                local descOk, descResult = pcall(GetSpellDescription, spellID)
                if descOk and descResult then
                    description = descResult
                end
            end

            local node = {
                name = tName,
                icon = extractIconName(tIcon),
                row = tier,
                col = column,
                maxRank = maxRank,
                description = description,
                spellID = spellID,
            }
            table.insert(tab.nodes, node)
        end

        table.insert(data.tabs, tab)
    end

    if not TalentExtractor_Export then TalentExtractor_Export = {} end
    TalentExtractor_Export[englishClass] = data

    local totalNodes = 0
    for _, tab in ipairs(data.tabs) do
        totalNodes = totalNodes + #tab.nodes
    end

    print(string.format("|cff00ff00[TE] 扫描完成! [%s] %d 天赋树, %d 节点",
        playerClass, #data.tabs, totalNodes))
    print("|cff00ff00[TE] 已保存到内存，请使用 /te export 写入 SavedVariables")

    return true
end

local function exportData()
    if not TalentExtractor_Export or next(TalentExtractor_Export) == nil then
        print("|cffff0000[TE] 没有数据，请先使用 /te scan")
        return
    end

    local classCount = 0
    local tabCount = 0
    local nodeCount = 0
    for classFile, classData in pairs(TalentExtractor_Export) do
        classCount = classCount + 1
        for _, tab in ipairs(classData.tabs) do
            tabCount = tabCount + 1
            nodeCount = nodeCount + #tab.nodes
        end
    end

    print(string.format("|cffffff00[TE] 导出完成! %d 职业, %d 天赋树, %d 节点",
        classCount, tabCount, nodeCount))
    print("|cffffff00[TE] 关闭游戏后，运行 Python 脚本处理数据")
    print("|cffff0000[TE] 继续扫描其他职业，或者输入 /te reload 重新加载后继续")

    ReloadUI()
end

local function showHelp()
    print("|cffffcc00--- TalentExtractor v1.0 ---")
    print("  /te scan    - 扫描当前职业天赋(需10级+)")
    print("  /te export  - 保存所有已扫描数据并重载界面")
    print("  /te status  - 查看已扫描的职业")
    print("  /te reset   - 清空所有已扫描数据")
end

local function showStatus()
    if not TalentExtractor_Export or next(TalentExtractor_Export) == nil then
        print("|cffffcc00[TE] 尚未扫描任何职业")
        return
    end

    print("|cffffcc00[TE] 已扫描的职业:")
    local list = {}
    for classFile, classData in pairs(TalentExtractor_Export) do
        local nodeCount = 0
        for _, tab in ipairs(classData.tabs) do
            nodeCount = nodeCount + #tab.nodes
        end
        table.insert(list, string.format("  %s (%s) - %d 天赋树, %d 节点",
            classData.className, classFile, #classData.tabs, nodeCount))
    end
    table.sort(list)
    for _, entry in ipairs(list) do
        print(entry)
    end
    print(string.format("|cff00ff00共 %d 个职业", #list))
end

local function resetData()
    TalentExtractor_Export = nil
    print("|cffffff00[TE] 已清空所有扫描数据")
end

frame:RegisterEvent("ADDON_LOADED")
frame:SetScript("OnEvent", function(self, event, arg1)
    if event == "ADDON_LOADED" and arg1 == addonName then
        if not TalentExtractor_Export then TalentExtractor_Export = {} end

        print("|cff00ff00TalentExtractor 加载成功!|r")
        print("  /te scan - 扫描当前职业天赋数据")
        print("  /te export - 导出所有扫描数据")
    end
end)

SLASH_TE1 = "/te"
SlashCmdList["TE"] = function(msg)
    msg = string.lower(msg or "")
    msg = string.gsub(msg, "^%s+", "")
    msg = string.gsub(msg, "%s+$", "")

    if msg == "" then
        showHelp()
    elseif msg == "scan" then
        scanCurrentClass()
    elseif msg == "export" then
        exportData()
    elseif msg == "status" then
        showStatus()
    elseif msg == "reset" then
        resetData()
    else
        print("|cffff0000[TE] 未知命令: " .. msg)
        showHelp()
    end
end