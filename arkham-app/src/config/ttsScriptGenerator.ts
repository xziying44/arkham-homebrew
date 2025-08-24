// TTS脚本生成工具
export interface PhaseButton {
  id: string;
  label: string;
  color: string;
}

export interface PhaseButtonConfig {
  buttons: PhaseButton[];
}

// 按钮标签映射
export const buttonLabelOptions = [
  { value: 'b', label: '🔍 探求者', emoji: '🔍' },
  { value: 'c', label: '🧘 潜修者', emoji: '🧘' },
  { value: 'd', label: '🚶 流浪者', emoji: '🚶' },
  { value: 'e', label: '🏕️ 生存者', emoji: '🏕️' },
  { value: 'f', label: '🧠 脑', emoji: '🧠' },
  { value: 'g', label: '📚 书', emoji: '📚' },
  { value: 'h', label: '👊 拳', emoji: '👊' },
  { value: 'i', label: '🦶 脚', emoji: '🦶' },
  { value: 'j', label: '❓ ?', emoji: '❓' },
  { value: 'k', label: '⭐ 旧印', emoji: '⭐' },
  { value: 'l', label: '⚖️ 中立', emoji: '⚖️' },
  { value: 'm', label: '💀 骷髅', emoji: '💀' },
  { value: 'n', label: '👤 异教徒', emoji: '👤' },
  { value: 'o', label: '📜 石板', emoji: '📜' },
  { value: 'p', label: '👹 古神', emoji: '👹' },
  { value: 'q', label: '🐙 触手', emoji: '🐙' },
  { value: 'r', label: '🕵️ 调查员', emoji: '🕵️' },
  { value: 's', label: '🎯 弱点', emoji: '🎯' },
  { value: 't', label: '➡️ 启动', emoji: '➡️' },
  { value: 'u', label: '⭕ 反应', emoji: '⭕' },
  { value: 'v', label: '⚡ 免费', emoji: '⚡' },
  { value: 'w', label: '🔵 点', emoji: '🔵' },
  { value: 'y', label: '🌑 诅咒', emoji: '🌑' },
  { value: 'z', label: '🌟 祝福', emoji: '🌟' }
];

// 预定义颜色选项
export const colorOptions = [
  { value: '#ffffff', label: '⚪ 白色' },
  { value: '#ff7800', label: '🟠 橙色' },
  { value: '#e011ff', label: '🟣 紫色' },
  { value: '#ffe400', label: '🟡 黄色' },
  { value: '#ff0000', label: '🔴 红色' },
  { value: '#00ff00', label: '🟢 绿色' },
  { value: '#0066ff', label: '🔵 蓝色' },
  { value: '#333333', label: '⚫ 黑色' },
  { value: '#888888', label: '🩶 灰色' },
  { value: '#8B4513', label: '🟤 棕色' }
];

// 默认按钮配置
export const defaultPhaseButtons: PhaseButton[] = [
  { id: 'Mythos', label: 'u', color: '#ffffff' },
  { id: 'Investigation', label: 'u', color: '#ff7800' },
  { id: 'Enemy', label: 'u', color: '#e011ff' },
  { id: 'Upkeep', label: 'u', color: '#ffe400' }
];

// 生成阶段按钮脚本的buttonParams部分
export function generateButtonParams(config: PhaseButtonConfig): string {
  const labels = config.buttons.map(btn => `"${btn.label}"`).join(', ');
  const ids = config.buttons.map(btn => `"${btn.id}"`).join(', ');
  const colors = config.buttons.map(btn => `"${btn.color}"`).join(',\n    ');

  return `local buttonParams      = {
  buttonLabels = { ${labels} }, -- reaction symbols
  buttonIds    = { ${ids} },
  buttonColors = {
    ${colors}
  }
}`;
}

// 获取完整的每阶段脚本
export function generatePhaseButtonScript(config: PhaseButtonConfig): string {
  const baseScript = `-- Bundled by luabundle {"version":"1.6.0"}
local __bundle_require, __bundle_loaded, __bundle_register, __bundle_modules = (function(superRequire)
	local loadingPlaceholder = {[{}] = true}

	local register
	local modules = {}

	local require
	local loaded = {}

	register = function(name, body)
		if not modules[name] then
			modules[name] = body
		end
	end

	require = function(name)
		local loadedModule = loaded[name]

		if loadedModule then
			if loadedModule == loadingPlaceholder then
				return nil
			end
		else
			if not modules[name] then
				if not superRequire then
					local identifier = type(name) == 'string' and '\\"' .. name .. '\\"' or tostring(name)
					error('Tried to require ' .. identifier .. ', but no such module has been registered')
				else
					return superRequire(name)
				end
			end

			loaded[name] = loadingPlaceholder
			loadedModule = modules[name](require, loaded, register, modules)
			loaded[name] = loadedModule
		end

		return loadedModule
	end

	return require, loaded, register, modules
end)(nil)
__bundle_register("__root", function(require, _LOADED, __bundle_register, __bundle_modules)
require("playercards/CardsWithPhaseButtons")
end)
__bundle_register("playercards/CardsWithHelper", function(require, _LOADED, __bundle_register, __bundle_modules)
--[[ Library for cards that have helpers
This file is used to share code between cards with helpers.
It syncs the visibility of the helper with the option panel and
makes sure the card has the respective tag.
Additionally, it will call 'initialize()' and 'shutOff()'
in the parent file if they are present.

Instructions:
1) Define the global variables before requiring this file:
hasXML          = true  (whether the card has an XML display)
isHelperEnabled = false (default state of the helper, should be 'false')

2) Add "CardWithHelper" tag to .json for the card object itself.

3) Add \`if isHelperEnabled then updateDisplay() end\` to onLoad()

----------------------------------------------------------]]

-- forces a new state
function setHelperState(newState)
  if doNotTurnOff == true then return end
  isHelperEnabled = newState
  updateSave()
  updateDisplay()
end

-- toggles the current state
function toggleHelper(manual)
  if manual and isHelperEnabled == true then -- do not allow helper to be forced to turn on
    doNotTurnOff = true
  elseif manual and isHelperEnabled == false then -- return to default behavior
    doNotTurnOff = false
  end
  isHelperEnabled = not isHelperEnabled
  updateSave()
  updateDisplay()
end

-- updates the visibility and calls events (after a small delay to allow XML being set)
function updateDisplay()
  Wait.frames(actualDisplayUpdate, 5)
end

function actualDisplayUpdate()
  if isHelperEnabled then
    self.clearContextMenu()
    self.addContextMenuItem("Disable Helper", toggleHelper)
    if hasXML then self.UI.show("Helper") end
    if initialize then initialize() end
  else
    self.clearContextMenu()
    self.addContextMenuItem("Enable Helper", toggleHelper)
    if hasXML then self.UI.hide("Helper") end
    if shutOff then shutOff() end
  end
  if generateContextMenu then generateContextMenu() end
end

function onPickUp()
  setHelperState(false)
end
end)
__bundle_register("playercards/CardsWithPhaseButtons", function(require, _LOADED, __bundle_register, __bundle_modules)
require("playercards/CardsWithHelper")
local SideButtonCreator = require("util/SideButtonCreator")

-- intentionally global
hasXML                  = true
isHelperEnabled         = false

-- BUTTON_PARAMS_PLACEHOLDER --

local buttonIdToIndex   = {
  <!-- BUTTON_ID_INDEX_PLACEHOLDER -->
}

---------------------------------------------------------
-- general setup
---------------------------------------------------------

function updateSave()
  self.script_state = JSON.encode({ isHelperEnabled = isHelperEnabled })
end

function onLoad(savedData)
  self.addTag("CardWithHelper")
  self.addTag("DoInUpkeep")

  if savedData and savedData ~= "" then
    local loadedData = JSON.decode(savedData)
    isHelperEnabled = loadedData.isHelperEnabled
  end

  createHelperXML()

  if isHelperEnabled then
    updateDisplay()
  end
end

function createHelperXML()
  local xmlTable = SideButtonCreator.getXmlTable(buttonParams)
  self.UI.setXmlTable(xmlTable)
end

---------------------------------------------------------
-- main functionality
---------------------------------------------------------

-- sets the state for all buttons
function setUiState(params)
  for buttonId, state in pairs(params) do
    setStateForButton(state, buttonId)
  end
end

-- sets the state for a specific button
function setStateForButton(state, buttonId)
  -- if state is omitted, get it from the XML and toggle it
  if not state then
    state = (self.UI.getAttribute(buttonId, "buttonState") == "off")
  end

  local color = buttonParams.buttonColors[buttonIdToIndex[buttonId]]
  self.UI.setAttribute(buttonId, "color", state and color or "#353535E6")
  self.UI.setAttribute(buttonId, "textColor", state and "white" or "#A0A0A0")
  self.UI.setAttribute(buttonId, "buttonState", state and "on" or "off")
end

-- toggles the state for the clicked button
function onClick_sideButton(_, _, buttonId)
  setStateForButton(nil, buttonId)
end

-- called by the Upkeep function - sets all buttons to enabled
function doInUpkeep()
  for _, buttonId in ipairs(buttonParams.buttonIds) do
    setStateForButton(true, buttonId)
  end
end
end)
__bundle_register("util/SideButtonCreator", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local SideButtonCreator = {}

  -- generates the XML table for the defaults
  local function generateDefaults(buttonCount)
    local defaults = {
      tag = "Defaults",
      children = {
        {
          tag = "Button",
          attributes = {
            font          = "font_arkhamicons",
            fontSize      = "300",
            textAlignment = "UpperCenter", -- results in almost vertically centered reaction symbols
            onClick       = "onClick_sideButton"
          }
        },
        {
          tag = "TableLayout",
          attributes = {
            position            = "0 188 -40",
            rotation            = "0 0 90",
            height              = buttonCount * 400,
            width               = "700",
            scale               = "0.1 0.1 1",
            cellSpacing         = "70",
            cellPadding         = "0 6 6 6",
            cellBackgroundColor = "rgba(1,1,1,0)",
            rowBackgroundColor  = "rgba(0,0,0,0.666)"
          }
        }
      }
    }
    return defaults
  end

  -- main function - creates and returns the XML table for the side buttons
  function SideButtonCreator.getXmlTable(params)
    -- defaults for parameters
    params              = params or {}
    params.buttonCount  = params.buttonCount or <!-- BUTTON_COUNT -->
    params.buttonLabels = params.buttonLabels or {}
    params.buttonIds    = params.buttonIds or {}
    params.buttonColors = params.buttonColors or {}

    -- create the XML table
    local xmlTable      = {}

    -- get the defaults
    table.insert(xmlTable, generateDefaults(params.buttonCount))

    -- create the table layout
    local tableLayoutXml = {
      tag = "TableLayout",
      attributes = { id = "Helper", active = "false" },
      children = {}
    }

    -- add the buttons to it
    for i = 1, params.buttonCount do
      local buttonXml = {
        tag = "Row",
        attributes = { id = "Row" .. i },
        children = {
          {
            tag = "Cell",
            children = {
              {
                tag = "Button",
                attributes = {
                  buttonState = "on",
                  id          = params.buttonIds[i] or ("Button" .. i),
                  color       = params.buttonColors[i] or "white",
                  text        = params.buttonLabels[i] or ""
                }
              }
            }
          }
        }
      }

      table.insert(tableLayoutXml.children, buttonXml)
    end

    -- add to the XmlTable
    table.insert(xmlTable, tableLayoutXml)

    return xmlTable
  end

  return SideButtonCreator
end
end)
return __bundle_require("__root")`;

  // 生成buttonIdToIndex映射
  const buttonIdIndexMap = config.buttons
    .map((btn, index) => `  ${btn.id} = ${index + 1}`)
    .join(',\n');

  // 替换占位符
  let script = baseScript.replace('-- BUTTON_PARAMS_PLACEHOLDER --', generateButtonParams(config));
  script = script.replace('<!-- BUTTON_ID_INDEX_PLACEHOLDER -->', buttonIdIndexMap);
  script = script.replace('<!-- BUTTON_COUNT -->', config.buttons.length.toString());
  
  return script;
}

// 解析现有配置（从LuaScript中提取）
export function parsePhaseButtonConfig(luaScript: string): PhaseButtonConfig | null {
  try {
    // 提取buttonParams部分
    const buttonParamsMatch = luaScript.match(/local buttonParams\s*=\s*{[\s\S]*?}/);
    if (!buttonParamsMatch) return null;

    const buttonParamsStr = buttonParamsMatch[0];

    // 提取buttonLabels
    const labelsMatch = buttonParamsStr.match(/buttonLabels\s*=\s*{\s*([^}]+)\s*}/);
    const idsMatch = buttonParamsStr.match(/buttonIds\s*=\s*{\s*([^}]+)\s*}/);
    const colorsMatch = buttonParamsStr.match(/buttonColors\s*=\s*{[\s\S]*?}/);

    if (!labelsMatch || !idsMatch || !colorsMatch) return null;

    // 解析标签
    const labels = labelsMatch[1].split(',').map(s => s.trim().replace(/"/g, ''));
    const ids = idsMatch[1].split(',').map(s => s.trim().replace(/"/g, ''));
    
    // 解析颜色
    const colorsStr = colorsMatch[0];
    const colorMatches = colorsStr.match(/"#[a-fA-F0-9]{6}"/g);
    const colors = colorMatches ? colorMatches.map(s => s.replace(/"/g, '')) : [];

    // 构建按钮配置
    const buttons: PhaseButton[] = [];
    const maxLength = Math.max(labels.length, ids.length, colors.length);
    
    for (let i = 0; i < maxLength; i++) {
      buttons.push({
        id: ids[i] || `Button${i + 1}`,
        label: labels[i] || 'w',
        color: colors[i] || '#ffffff'
      });
    }

    return { buttons };
  } catch (error) {
    console.error('解析阶段按钮配置失败:', error);
    return null;
  }
}
