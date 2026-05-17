-- IconCollector - 装备图标收集插件 (Wrath 3.3.5 兼容版)
-- 遍历指定 item_id 列表，通过 GetItemInfo 获取游戏内的确切图标名
-- 结果保存在 IconCollectorDB SavedVariables 中
-- 用法: 登录游戏后输入 /ic scan 开始扫描
--       输入 /ic report 查看结果
--       输入 /ic export 输出Lua格式结果

local ADDON_NAME = "IconCollector"

-- 需要获取图标名的物品ID列表（270个）
local MISSING_ITEM_IDS = {
    19, 20, 30, 58, 62, 10813, 14495, 17534, 18433, 18621,
    20306, 20318, 20738, 21551, 200060, 200068, 200235, 200240,
    201699, 201993, 202195, 204385, 204982, 206272, 206392,
    206580, 206684, 206685, 206686, 206687, 206691, 206692,
    206693, 206694, 206697, 206699, 206700, 206701, 206702,
    206703, 206704, 206705, 206706, 206717, 206726, 206730,
    206731, 206732, 206733, 206734, 206735, 206736, 206737,
    206738, 206739, 206740, 206741, 206742, 206743, 206744,
    206745, 206746, 206747, 206748, 206750, 206751, 206752,
    206753, 206754, 206755, 206756, 206757, 206759, 206953,
    207097, 208157, 209515, 209558, 209585, 209587, 209588,
    209589,
    209603, 209627, 209629, 209630, 209631, 209633, 209635,
    209636, 209639, 209641, 209642, 209644, 209648, 209649,
    209650, 209652, 209654, 209655, 209660, 209661, 209662,
    209663, 209665, 209695, 209696, 209697, 209780, 209782,
    209783, 209784, 209785, 209786, 209787, 209789, 209790,
    209791, 209792, 209793, 209794, 209796, 209801, 209803,
    209804, 209807, 209808, 209809, 209810, 209811, 209812,
    209813, 209814, 209815, 209826, 209827, 209829, 209876,
    209877, 209945, 210047, 210135, 211082, 211206, 211207,
    211261, 211262, 211817, 211844, 211847, 211850, 211851,
    216696, 224002, 224375, 224376, 224377, 224378, 224379,
    224380, 224381, 224382, 224383, 226805, 226812, 231312,
    232614, 235464, 235561, 235562, 238339, 238340, 238341,
    238342, 238343, 242551, 245584, 245612, 245613, 246901,
    247893, 248263, 248398, 248753, 248754, 248945, 248946,
    248947, 248948, 248949, 248950, 249819, 249820, 249821,
    256035, 256052, 256054, 256056, 256068, 256069, 256070,
    256396, 258417, 258420, 258424, 258883, 260491, 260493,
    260494, 260495, 260500, 260502, 260503, 260504, 260505,
    260510, 260511, 260512, 260781, 260831, 263199, 263200,
    263201, 263204, 263207, 263514, 264161, 264167, 264198,
    264272, 264358, 264359, 264937, 264986, 265028, 265029, 265036,
    265069, 265070, 265333, 265335, 265340, 265342, 265343,
    265344, 265345, 265346, 265347, 265348, 265349, 265350,
    265351, 265352, 265353, 265354, 265355, 265356, 265492,
    265523, 265524, 265841, 265933, 265937, 265939, 265940,
    265942, 265944, 267335, 267340, 272955,
}

-- SavedVariables
IconCollectorDB = IconCollectorDB or {}

-- 扫描状态
local scanQueue = {}
local isScanning = false
local total = 0
local found = 0
local failed = 0

-- 使用 OnUpdate 模拟定时器（Wrath 3.3.5 没有 C_Timer.After）
local timerFrame = CreateFrame("Frame")
local lastProcessTime = 0
local SCAN_INTERVAL = 0.02

-- 从纹理路径中提取图标名
-- 例如 "Interface\\Icons\\inv_misc_questionmark" -> "inv_misc_questionmark"
local function ExtractIconName(texturePath)
    if not texturePath then return nil end
    local name = texturePath:match("([^\\]+)$")
    return name
end

-- 处理下一个物品
local function ProcessNextItem()
    if #scanQueue == 0 then
        isScanning = false
        timerFrame:SetScript("OnUpdate", nil)
        print(string.format("|cff00ff00[IconCollector] 扫描完成!|r 成功=%d  失败=%d  总计=%d", found, failed, total))
        return
    end

    local itemId = tremove(scanQueue, 1)
    local name, _, _, _, _, _, _, _, _, texture = GetItemInfo(itemId)

    if name and texture then
        local iconName = ExtractIconName(texture)
        if iconName then
            IconCollectorDB[tostring(itemId)] = iconName
            found = found + 1
        else
            failed = failed + 1
        end
    else
        -- 首次未命中，重新入队等待缓存
        tinsert(scanQueue, itemId)
        failed = failed + 1
    end

    -- 每处理5个输出一次进度
    if (found + failed) % 5 == 0 then
        print(string.format("[IconCollector] 进度: %d/%d", found + failed, total))
    end
end

-- OnUpdate 处理函数（轮询间隔执行）
timerFrame:SetScript("OnUpdate", function(self, elapsed)
    lastProcessTime = lastProcessTime + elapsed
    if lastProcessTime >= SCAN_INTERVAL then
        lastProcessTime = 0
        ProcessNextItem()
    end
end)
timerFrame:Hide()

-- 开始扫描
local function StartScan()
    if isScanning then
        print("|cffff0000[IconCollector] 扫描进行中，请勿重复启动|r")
        return
    end

    wipe(scanQueue)
    for _, itemId in ipairs(MISSING_ITEM_IDS) do
        tinsert(scanQueue, itemId)
    end

    total = #scanQueue
    found = 0
    failed = 0
    isScanning = true
    lastProcessTime = 0

    print(string.format("|cffffff00[IconCollector] 开始扫描 %d 个物品的图标...|r", total))
    timerFrame:Show()
end

-- 输出扫描报告
local function ShowReport()
    local count = 0
    for k, v in pairs(IconCollectorDB) do
        count = count + 1
    end
    print(string.format("|cff00ff00[IconCollector] 已收集 %d 个图标|r", count))
    if count > 0 then
        print("输入 /ic details 查看详情")
        print("输入 /ic export 导出Lua格式")
    end
end

-- 输出详细结果
local function ShowDetails()
    local sorted = {}
    for k, v in pairs(IconCollectorDB) do
        tinsert(sorted, {id = tonumber(k), icon = v})
    end
    sort(sorted, function(a, b) return a.id < b.id end)

    print("|cffffff00[IconCollector] 图标映射详情:|r")
    for _, entry in ipairs(sorted) do
        print(string.format("  [%d] = \"%s\"", entry.id, entry.icon))
    end
end

-- 导出为可导入的Lua格式
local function ExportResults()
    local sorted = {}
    for k, v in pairs(IconCollectorDB) do
        tinsert(sorted, {id = tonumber(k), icon = v})
    end
    sort(sorted, function(a, b) return a.id < b.id end)

    print("|cffffff00[IconCollector] === 导出结果 (可复制) ===|r")
    print("local icon_mapping = {")
    for _, entry in ipairs(sorted) do
        print(string.format("    [%d] = \"%s\",", entry.id, entry.icon))
    end
    print("}")
    print("|cffffff00[IconCollector] === 导出结束 ===|r")
end

-- 清空已有结果重新扫描
local function ResetAndRescan()
    wipe(IconCollectorDB)
    print("|cffffff00[IconCollector] 已清空历史记录，开始重新扫描...|r")
    StartScan()
end

-- 注册斜杠命令
SLASH_ICONCOLLECTOR1 = "/iconcollector"
SLASH_ICONCOLLECTOR2 = "/ic"
SlashCmdList["ICONCOLLECTOR"] = function(msg)
    local cmd = msg:trim():lower()
    if cmd == "scan" then
        StartScan()
    elseif cmd == "report" or cmd == "" then
        ShowReport()
    elseif cmd == "details" then
        ShowDetails()
    elseif cmd == "export" then
        ExportResults()
    elseif cmd == "reset" then
        ResetAndRescan()
    elseif cmd == "help" then
        print("|cffffff00[IconCollector] 命令列表:|r")
        print("  /ic            - 显示报告")
        print("  /ic scan       - 开始扫描")
        print("  /ic details    - 显示详细结果")
        print("  /ic export     - 导出Lua格式")
        print("  /ic reset      - 清空并重新扫描")
    else
        print("|cffff0000未知命令，输入 /ic help 查看帮助|r")
    end
end

-- 插件加载完成后的初始化
local loadFrame = CreateFrame("Frame")
loadFrame:RegisterEvent("ADDON_LOADED")
loadFrame:SetScript("OnEvent", function(self, event, arg1)
    if arg1 ~= ADDON_NAME then return end

    local count = 0
    for k, v in pairs(IconCollectorDB) do
        count = count + 1
    end

    if count > 0 then
        print(string.format("|cff00ff00[IconCollector] 已加载|r 当前已有 %d 个图标记录，输入 /ic report 查看详情", count))
    else
        print("|cff00ff00[IconCollector] 已加载|r 输入 /ic scan 开始扫描图标，输入 /ic help 查看命令")
    end

    self:UnregisterEvent("ADDON_LOADED")
end)