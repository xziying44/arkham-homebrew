-- Bundled by luabundle {"version":"1.6.0"}
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
					local identifier = type(name) == 'string' and '\"' .. name .. '\"' or tostring(name)
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
require("playercards/cards/SealTemplate")
end)
__bundle_register("chaosbag/BlessCurseManagerApi", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local BlessCurseManagerApi = {}
  local guidReferenceApi = require("core/GUIDReferenceApi")

  local function getManager()
    return guidReferenceApi.getObjectByOwnerAndType("Mythos", "BlessCurseManager")
  end

  -- removes all taken tokens and resets the counts
  BlessCurseManagerApi.removeTakenTokensAndReset = function()
    local BlessCurseManager = getManager()
    Wait.time(function() BlessCurseManager.call("removeTakenTokens", "Bless") end, 0.05)
    Wait.time(function() BlessCurseManager.call("removeTakenTokens", "Curse") end, 0.10)
    Wait.time(function() BlessCurseManager.call("doReset", "White") end, 0.15)
  end

  -- updates the internal count (called by cards that seal bless/curse tokens)
  ---@param type string Type of chaos token ("Bless" or "Curse")
  ---@param guid string GUID of the token
  ---@param silent? boolean Whether or not to hide messages
  BlessCurseManagerApi.sealedToken = function(type, guid, silent)
    getManager().call("sealedToken", { type = type, guid = guid, silent = silent })
  end

  -- updates the internal count (called by cards that seal bless/curse tokens)
  ---@param type string Type of chaos token ("Bless" or "Curse")
  ---@param guid string GUID of the token
  ---@param fromBag? boolean Whether or not token was just drawn from the chaos bag
  ---@param silent? boolean Whether or not to hide messages
  BlessCurseManagerApi.releasedToken = function(type, guid, fromBag, silent)
    getManager().call("releasedToken", { type = type, guid = guid, fromBag = fromBag, silent = silent })
  end

  -- updates the internal count (called by cards that seal bless/curse tokens)
  ---@param type string Type of chaos token ("Bless" or "Curse")
  ---@param guid string GUID of the token
  BlessCurseManagerApi.returnedToken = function(type, guid)
    getManager().call("returnedToken", { type = type, guid = guid })
  end

  -- broadcasts the current status for bless/curse tokens
  ---@param playerColor string Color of the player to show the broadcast to
  BlessCurseManagerApi.broadcastStatus = function(playerColor)
    getManager().call("broadcastStatus", playerColor)
  end

  -- removes all bless / curse tokens from the chaos bag and play
  ---@param playerColor string Color of the player to show the broadcast to
  BlessCurseManagerApi.removeAll = function(playerColor)
    getManager().call("doRemove", playerColor)
  end

  -- adds bless / curse sealing to the hovered card
  ---@param playerColor string Color of the player to show the broadcast to
  ---@param hoveredObject tts__Object Hovered object
  ---@param noCurse? boolean True if just Bless sealing should be added (Parallel Mateo)
  BlessCurseManagerApi.addBlurseSealingMenu = function(playerColor, hoveredObject, noCurse)
    getManager().call("addMenuOptions", { playerColor = playerColor, hoveredObject = hoveredObject, noCurse = noCurse })
  end

  -- adds bless / curse to the chaos bag
  ---@param tokenType string Type of chaos token ("Bless" or "Curse")
  ---@param playerColor? string Color of the triggering player
  BlessCurseManagerApi.addToken = function(tokenType, playerColor)
    getManager().call("callFunctionFromApi", { tokenType = tokenType, playerColor = playerColor, remove = false })
  end

  -- removes bless / curse from the chaos bag
  ---@param tokenType string Type of chaos token ("Bless" or "Curse")
  ---@param playerColor? string Color of the triggering player
  BlessCurseManagerApi.removeToken = function(tokenType, playerColor)
    getManager().call("callFunctionFromApi", { tokenType = tokenType, playerColor = playerColor, remove = true })
  end

  BlessCurseManagerApi.getBlessCurseInBag = function()
    return getManager().call("getBlessCurseInBag", {})
  end

  return BlessCurseManagerApi
end
end)
__bundle_register("chaosbag/ChaosBagApi", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local ChaosBagApi = {}

  -- respawns the chaos bag with a new state of tokens
  ---@param tokenList table List of chaos token ids
  ChaosBagApi.setChaosBagState = function(tokenList)
    Global.call("setChaosBagState", tokenList)
  end

  -- returns a Table List of chaos token ids in the current chaos bag
  -- requires copying the data into a new table because TTS is weird about handling table return values in Global
  ChaosBagApi.getChaosBagState = function()
    local chaosBagContentsCatcher = Global.call("getChaosBagState")
    local chaosBagContents = {}
    for _, v in ipairs(chaosBagContentsCatcher) do
      table.insert(chaosBagContents, v)
    end
    return chaosBagContents
  end

  -- checks scripting zone for chaos bag (also called by a lot of objects!)
  ChaosBagApi.findChaosBag = function()
    return Global.call("findChaosBag")
  end

  -- returns a table of object references to the tokens in play (does not include sealed tokens!)
  ChaosBagApi.getTokensInPlay = function()
    return Global.call("getChaosTokensinPlay")
  end

  -- returns all sealed tokens on cards to the chaos bag
  ---@param playerColor string Color of the player to show the broadcast to
  ---@param filterName? string Name of the token to release
  ---@param silent? boolean Whether or not to hide messages
  ChaosBagApi.releaseAllSealedTokens = function(playerColor, filterName, silent)
    Global.call("releaseAllSealedTokens", { playerColor = playerColor, filterName = filterName, silent = silent })
  end

  -- returns all drawn tokens to the chaos bag
  ChaosBagApi.returnChaosTokens = function()
    Global.call("returnChaosTokens")
  end

  -- removes the specified chaos token from the chaos bag
  ---@param id string ID of the chaos token
  ChaosBagApi.removeChaosToken = function(id)
    Global.call("removeChaosToken", id)
  end

  -- returns a chaos token to the bag and calls all relevant functions
  ---@param token tts__Object Chaos token to return
  ---@param fromBag boolean whether or not the token to return was in the middle of being drawn (true) or elsewhere (false)
  ChaosBagApi.returnChaosTokenToBag = function(token, fromBag)
    Global.call("returnChaosTokenToBag", { token = token, fromBag = fromBag })
  end

  -- spawns the specified chaos token and puts it into the chaos bag
  ---@param id string ID of the chaos token
  ChaosBagApi.spawnChaosToken = function(id)
    Global.call("spawnChaosToken", id)
  end

  -- Checks to see if the chaos bag can be manipulated.  If a player is searching the bag when tokens
  -- are drawn or replaced a TTS bug can cause those tokens to vanish.  Any functions which change the
  -- contents of the bag should check this method before doing so.
  -- This method will broadcast a message to all players if the bag is being searched.
  ---@return any: True if the bag is manipulated, false if it should be blocked.
  ChaosBagApi.canTouchChaosTokens = function()
    return Global.call("canTouchChaosTokens")
  end

  ChaosBagApi.activeRedrawEffect = function(validTokens, invalidTokens, returnToPool, drawSpecificToken)
    Global.call("activeRedrawEffect", {
      validTokens = validTokens,
      invalidTokens = invalidTokens,
      returnToPool = returnToPool,
      drawSpecificToken = drawSpecificToken
    })
  end

  ChaosBagApi.getReadableTokenName = function(tokenName)
    return Global.call("getReadableTokenName", tokenName)
  end

  ChaosBagApi.getChaosTokenName = function(chosenToken)
    return Global.call("getChaosTokenName", chosenToken)
  end

  -- draws a chaos token to a playermat
  ---@param mat tts__Object|string Playermat that triggered this (either object or matColor)
  ---@param drawAdditional boolean Controls whether additional tokens should be drawn
  ---@param tokenType? string Name of token (e.g. "Bless") to be drawn from the bag
  ---@param guidToBeResolved? string GUID of the sealed token to be resolved instead of drawing a token from the bag
  ---@param takeParameters? table Position and rotation of the location where the new token should be drawn to, usually to replace a returned token
  ---@return tts__Object: Object reference to the token that was drawn
  ChaosBagApi.drawChaosToken = function(mat, drawAdditional, tokenType, guidToBeResolved, takeParameters)
    return Global.call("drawChaosToken", {
      mat              = mat,
      drawAdditional   = drawAdditional,
      tokenType        = tokenType,
      guidToBeResolved = guidToBeResolved,
      takeParameters   = takeParameters
    })
  end

  -- returns a Table List of chaos token ids in the current chaos bag
  -- requires copying the data into a new table because TTS is weird about handling table return values in Global
  ChaosBagApi.getIdUrlMap = function()
    return Global.getTable("ID_URL_MAP")
  end

  return ChaosBagApi
end
end)
__bundle_register("core/GUIDReferenceApi", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local GUIDReferenceApi = {}

  local function getGuidHandler()
    return getObjectFromGUID("123456")
  end

  -- Returns the matching object
  ---@param owner string Parent object for this search
  ---@param type string Type of object to search for
  ---@return any: Object reference to the matching object
  GUIDReferenceApi.getObjectByOwnerAndType = function(owner, type)
    return getGuidHandler().call("getObjectByOwnerAndType", { owner = owner, type = type })
  end

  -- Returns all matching objects as a table with references
  ---@param type string Type of object to search for
  ---@return table: List of object references to matching objects
  GUIDReferenceApi.getObjectsByType = function(type)
    return getGuidHandler().call("getObjectsByType", type)
  end

  -- Returns all matching objects as a table with references
  ---@param owner string Parent object for this search
  ---@return table: List of object references to matching objects
  GUIDReferenceApi.getObjectsByOwner = function(owner)
    return getGuidHandler().call("getObjectsByOwner", owner)
  end

  -- Sends new information to the reference handler to edit the main index (if type/guid are omitted, entry will be removed)
  ---@param owner string Parent of the object
  ---@param type? string Type of the object
  ---@param guid? string GUID of the object
  GUIDReferenceApi.editIndex = function(owner, type, guid)
    return getGuidHandler().call("editIndex", {
      owner = owner,
      type = type,
      guid = guid
    })
  end

  -- Returns the owner of an object or the object it's located on
  ---@param object tts__GameObject Object for this search
  ---@return string: Parent of the object or object it's located on
  GUIDReferenceApi.getOwnerOfObject = function(object)
    return getGuidHandler().call("getOwnerOfObject", object)
  end

  -- Remove object
  ---@param owner string Parent of the object
  ---@param type string Type of the object
  GUIDReferenceApi.removeObjectByOwnerAndType = function(owner, type)
    return getGuidHandler().call("removeObjectByOwnerAndType", {
      owner = owner,
      type = type
    })
  end

  return GUIDReferenceApi
end
end)
__bundle_register("playercards/CardsThatSealTokens", function(require, _LOADED, __bundle_register, __bundle_modules)
--[[ Library for cards that seal tokens
This file is used to add sealing option to cards' context menu.
NOTE: all cards are allowed to release a single token to enable Hallow and A Watchful Peace,
and to release all sealed tokens to allow for cards that might leave play with sealed tokens on them.
Valid options (set before requiring this file):

MAX_SEALED          --@type: number (maximum number of tokens allowable by the card to be sealed)
  - required for all cards
  - if MAX_SEALED is more than 1, then an XML label is created for the topmost token indicating the number of sealed tokens
  - gives an error if user tries to seal additional tokens on the card
  - example usage: "The Chthonian Stone"
    > MAX_SEALED = 1

UPDATE_ON_HOVER     --@type: boolean
  - automatically updates the context menu options when the card is hovered
  - the "Read Bag" function reads the content of the chaos bag to update the context menu
  - example usage: "Unrelenting" (to only display valid tokens)

KEEP_OPEN           --@type: boolean
- meant for cards that seal single tokens multiple times (one by one)
- makes the context menu stay open after selecting an option
- example usage: "Unrelenting"

SHOW_MULTI_RELEASE  --@type: number (maximum amount of tokens to release at once)
  - enables an entry in the context menu
  - this entry allows releasing of multiple tokens at once, to the maximum number
  - does not fail if there are fewer than the maximum sealed
  - example usage: "Nephthys" (to release up to 3 bless tokens at once)

SHOW_MULTI_RETURN   --@type: number (amount of tokens to return to pool at once)
  - enables an entry in the context menu
  - this entry allows returning tokens to the token pool
  - fails if not enough tokens are sealed
  - example usage: "Nephthys" (to return 3 bless tokens at once)

SHOW_RETURN_ALL   --@boolean:
  - enables an entry in the context menu
  - this entry allows returning all sealed tokens to the token pool
  - example usage: "Radiant Smite" (to return whatever number of bless tokens that are sealed at once)

SHOW_MULTI_SEAL     --@type: number (amount of tokens to seal at once)
  - enables an entry in the context menu
  - this entry allows sealing of multiple tokens at once
  - example usage: "Holy Spear" (to seal two bless tokens at once)

VALID_TOKENS        --@type: table ([tokenName] = true)
  - this table defines which tokens should be abled to be sealed
  - needs to be defined for each card -> even if empty
  - example usage: "The Chthonian Stone"
    > VALID_TOKENS = {
    >   ["Skull"]       = true,
    >   ["Cultist"]     = true,
    >   ["Tablet"]      = true,
    >   ["Elder Thing"] = true,
    > }

INVALID_TOKENS      --@type: table ([tokenName] = true)
  - this table defines which tokens are invalid for sealing
  - only needs to be defined if needed
  - usually combined with empty "VALID_TOKENS" table
  - example usage: "Protective Incantation" (not allowed to seal Auto-fail)

----------------------------------------------------------
Example 1: Crystalline Elder Sign
This card can only seal the "+1" or "Elder Sign" token,
it does not need specific options for multi-sealing or releasing.
Thus it should be implemented like this:
  > VALID_TOKENS = {
  >   ["+1"] = true,
  >   ["Elder Sign"] = true
  > }
  > MAX_SEALED = 1
  > require...
----------------------------------------------------------
Example 2: Holy Spear
This card features the following abilities (just listing the relevant parts):
- releasing a single bless token
- sealing two bless tokens
Thus it should be implemented like this:
  > VALID_TOKENS = {
  >   ["Bless"] = true
  > }
  > SHOW_MULTI_SEAL = 2
  > MAX_SEALED = 10
  > require...
----------------------------------------------------------]]

local blessCurseManagerApi = require("chaosbag/BlessCurseManagerApi")
local chaosBagApi          = require("chaosbag/ChaosBagApi")
local playermatApi         = require("playermat/PlayermatApi")
local tokenArrangerApi     = require("tokens/TokenArrangerApi")

local sealedTokens         = {}
local ID_URL_MAP           = {}
local tokensInBag          = {}

-- XML background color for each token for label when stacked
local tokenColor           = {
  ["Skull"]       = "#4A0400E6",
  ["Cultist"]     = "#173B0BE6",
  ["Tablet"]      = "#1D2238E6",
  ["Elder Thing"] = "#4D2331E6",
  ["Auto-fail"]   = "#9B0004E6",
  ["Bless"]       = "#9D702CE6",
  ["Curse"]       = "#633A84E6",
  ["Frost"]       = "#404450E6",
  ["Elder Sign"]  = "#50A8CEE6",
  [""]            = "#77674DE6"
}

function updateSave()
  updateStackSize()
  self.script_state = JSON.encode(sealedTokens)
end

function onLoad(savedData)
  -- if MAX_SEALED is not set, default to 99
  MAX_SEALED = MAX_SEALED or 99

  -- verify sealed tokens
  for _, guid in ipairs(JSON.decode(savedData) or {}) do
    local token = getObjectFromGUID(guid)
    if token ~= nil then
      table.insert(sealedTokens, guid)
    end
  end

  ID_URL_MAP = chaosBagApi.getIdUrlMap()
  generateContextMenu()
  updateStackSize()
  self.addTag("CardThatSeals")
end

-- i18n menu labels (injected by generator)
-- MENU_RELEASE_ONE_PLACEHOLDER --
-- MENU_RELEASE_ONE_PREFIX_PLACEHOLDER --
-- MENU_RELEASE_ALL_PLACEHOLDER --
-- MENU_RELEASE_MULTI_PREFIX_PLACEHOLDER --
-- MENU_RETURN_MULTI_PREFIX_PLACEHOLDER --
-- MENU_TOKEN_SUFFIX_PLACEHOLDER --
-- MENU_RETURN_ALL_PLACEHOLDER --
-- MENU_RESOLVE_PREFIX_PLACEHOLDER --
-- MENU_RESOLVE_ONE_PLACEHOLDER --
-- MENU_RESOLVE_ONE_PREFIX_PLACEHOLDER --
-- MENU_SEAL_PREFIX_PLACEHOLDER --
-- MENU_SEAL_MULTI_PREFIX_PLACEHOLDER --
-- MENU_SEAL_MULTI_INFIX_PLACEHOLDER --
-- TOKEN_DISPLAY_FUNC_PLACEHOLDER --
-- TOKEN_DISPLAY_OR_DEFAULT_FUNC_PLACEHOLDER --
-- GENERIC_TOKEN_LABEL_PLACEHOLDER --

-- builds the context menu
function generateContextMenu()
  -- determine if exactly one valid token type is configured
  local SINGLE_VALID_TOKEN = nil
  for k, _ in pairs(VALID_TOKENS) do
    if SINGLE_VALID_TOKEN == nil then
      SINGLE_VALID_TOKEN = k
    else
      SINGLE_VALID_TOKEN = false -- more than one
      break
    end
  end

  local releaseOneLabel
  if SINGLE_VALID_TOKEN and type(SINGLE_VALID_TOKEN) == 'string' then
    releaseOneLabel = MENU_RELEASE_ONE_PREFIX .. TOKEN_DISPLAY(SINGLE_VALID_TOKEN)
  else
    releaseOneLabel = MENU_RELEASE_ONE
  end
  self.addContextMenuItem(releaseOneLabel, releaseOneToken)

  -- conditional release options
  if MAX_SEALED > 1 then
    self.addContextMenuItem(MENU_RELEASE_ALL, releaseAllTokens)
  end

  if SHOW_MULTI_RELEASE then
    self.addContextMenuItem(MENU_RELEASE_MULTI_PREFIX .. SHOW_MULTI_RELEASE .. MENU_TOKEN_SUFFIX, releaseMultipleTokens)
  end

  if RESOLVE_TOKEN then
    local resolveOneLabel
    if SINGLE_VALID_TOKEN and type(SINGLE_VALID_TOKEN) == 'string' then
      resolveOneLabel = MENU_RESOLVE_ONE_PREFIX .. TOKEN_DISPLAY(SINGLE_VALID_TOKEN)
    else
      resolveOneLabel = MENU_RESOLVE_ONE
    end
    self.addContextMenuItem(resolveOneLabel, resolveSealed)
  end

  if SHOW_MULTI_RETURN then
    self.addContextMenuItem(MENU_RETURN_MULTI_PREFIX .. SHOW_MULTI_RETURN .. MENU_TOKEN_SUFFIX, returnMultipleTokens)
  end

  if SHOW_RETURN_ALL then
    self.addContextMenuItem(MENU_RETURN_ALL, returnAllTokens)
  end

  -- main context menu options to seal tokens
  for _, map in pairs(ID_URL_MAP) do
    if (VALID_TOKENS[map.name] ~= nil) or (UPDATE_ON_HOVER and tokensInBag[map.name] and INVALID_TOKENS and not INVALID_TOKENS[map.name]) then
      if not SHOW_MULTI_SEAL then
        self.addContextMenuItem(MENU_SEAL_PREFIX .. TOKEN_DISPLAY(map.name), function(playerColor)
          self.removeFromPlayerSelection(playerColor)
          if not chaosBagApi.canTouchChaosTokens() then return end
          sealToken(map.name, playerColor)
        end, KEEP_OPEN)
      else
        self.addContextMenuItem(MENU_SEAL_MULTI_PREFIX .. SHOW_MULTI_SEAL .. MENU_SEAL_MULTI_INFIX .. TOKEN_DISPLAY(map.name), function(playerColor)
          self.removeFromPlayerSelection(playerColor)
          if not chaosBagApi.canTouchChaosTokens() then return end
          readBag()
          local allowed = true
          local notFound

          for name, _ in pairs(VALID_TOKENS) do
            if (tokensInBag[name] or 0) < SHOW_MULTI_SEAL then
              allowed = false
              notFound = name
            end
          end

          if allowed then
            for i = SHOW_MULTI_SEAL, 1, -1 do
              sealToken(map.name, playerColor)
            end
          else
            printToColor("Not enough " .. notFound .. " tokens in the chaos bag.", playerColor)
          end
        end)
      end
    end
  end
end

-- generates a list of chaos tokens that is in the chaos bag
function readBag()
  local chaosbag = chaosBagApi.findChaosBag()
  tokensInBag = {}

  for _, token in ipairs(chaosbag.getObjects()) do
    tokensInBag[token.name] = (tokensInBag[token.name] or 0) + 1
  end
end

function resetSealedTokens()
  sealedTokens = {}
  updateSave()
end

-- native event from TTS - used to update the context menu for cards like "Unrelenting"
function onHover()
  if UPDATE_ON_HOVER then
    readBag()
    self.clearContextMenu()
    generateContextMenu()
  end
end

-- seals the named token on this card
function sealToken(name, playerColor)
  if #sealedTokens >= MAX_SEALED then
    printToColor("Cannot seal any more tokens on this card", playerColor, "Red")
    return
  end
  if not chaosBagApi.canTouchChaosTokens() then return end
  local chaosbag = chaosBagApi.findChaosBag()
  for i, obj in ipairs(chaosbag.getObjects()) do
    if obj.name == name then
      return chaosbag.takeObject({
        position = self.getPosition() + Vector(0, 0.5 + 0.1 * #sealedTokens, 0),
        rotation = self.getRotation(),
        index = i - 1,
        smooth = false,
        callback_function = function(token)
          local guid = token.getGUID()
          table.insert(sealedTokens, guid)
          tokenArrangerApi.layout()
          if name == "Bless" or name == "Curse" then
            blessCurseManagerApi.sealedToken(name, guid)
          end
          -- destroy XML on just covered token
          if #sealedTokens > 1 then
            local coveredToken = getObjectFromGUID(sealedTokens[#sealedTokens - 1])
            if coveredToken ~= nil then
              coveredToken.UI.setXml("")
            else
              table.remove(sealedTokens, #sealedTokens - 1)
            end
          end
          updateSave()
        end
      })
    end
  end
  printToColor(name .. " token not found in chaos bag", playerColor)
end

-- release the last sealed token
function releaseOneToken(playerColor)
  self.removeFromPlayerSelection(playerColor)
  if not chaosBagApi.canTouchChaosTokens() then return end
  if #sealedTokens == 0 then
    printToColor("No sealed token(s) found", playerColor)
  else
    printToColor("Releasing token", playerColor)

    -- make list of token names
    local tokenNames = {}
    local differentNames = 0
    for _, guid in ipairs(sealedTokens) do
      local token = getObjectFromGUID(guid)
      if token ~= nil then
        local name = token.getName()
        if tokenNames[name] == nil then
          differentNames = differentNames + 1
        end
        tokenNames[name] = guid
      end
    end

    -- if there are multiple tokens, ask the player to choose
    if differentNames < 2 then
      putTokenAway(table.remove(sealedTokens))
      updateSave()
    else
      local choices = {}
      for name, _ in pairs(tokenNames) do
        table.insert(choices, name)
      end
      Player[playerColor].showOptionsDialog("Choose token to release:", choices, 1, function(optionText, optionIndex)
        for i = #sealedTokens, 1, -1 do
          local token = getObjectFromGUID(sealedTokens[i])
          if token ~= nil and token.getName() == optionText then
            putTokenAway(table.remove(sealedTokens, i))
            updateSave()
            break
          end
        end
      end)
    end
  end
  Player[playerColor].clearSelectedObjects()
end

-- release up to multiple tokens at once with no minimum
function releaseMultipleTokens(playerColor)
  self.removeFromPlayerSelection(playerColor)
  if not chaosBagApi.canTouchChaosTokens() then return end
  if #sealedTokens == 0 then
    printToColor("Not enough tokens sealed.", playerColor)
    return
  end

  local numRemoved = SHOW_MULTI_RELEASE
  if #sealedTokens < SHOW_MULTI_RELEASE then
    numRemoved = #sealedTokens
  end

  for i = 1, numRemoved do
    putTokenAway(table.remove(sealedTokens))
  end
  updateSave()
  printToColor("Releasing " .. numRemoved .. " tokens", playerColor)
  Player[playerColor].clearSelectedObjects()
end

function releaseAllTokensWrapper(params)
  releaseAllTokens(params.playerColor, _, _, params.filterName, params.silent)
end

-- releases all sealed tokens
function releaseAllTokens(playerColor, _, _, filterName, silent)
  self.removeFromPlayerSelection(playerColor)
  if not chaosBagApi.canTouchChaosTokens() then return end
  if #sealedTokens == 0 then
    if not silent then
      printToColor("No sealed token(s) found", playerColor)
    end
  else
    if not silent then
      printToColor("Releasing token(s)", playerColor)
    end

    for i = #sealedTokens, 1, -1 do
      local success = putTokenAway(sealedTokens[i], filterName, silent)
      if success then
        table.remove(sealedTokens, i)
      end
    end

    updateSave()
  end
  Player[playerColor].clearSelectedObjects()
end

-- returns multiple tokens at once to the token pool (with minimum)
function returnMultipleTokens(playerColor)
  self.removeFromPlayerSelection(playerColor)
  if not chaosBagApi.canTouchChaosTokens() then return end
  if SHOW_MULTI_RETURN <= #sealedTokens then
    for i = 1, SHOW_MULTI_RETURN do
      returnToken(table.remove(sealedTokens))
    end
    updateSave()
    printToColor("Returning " .. SHOW_MULTI_RETURN .. " tokens to the token pool", playerColor)
  else
    printToColor("Not enough tokens sealed.", playerColor)
  end
  Player[playerColor].clearSelectedObjects()
end

-- returns all sealed tokens to the token pool
function returnAllTokens(playerColor)
  self.removeFromPlayerSelection(playerColor)
  if not chaosBagApi.canTouchChaosTokens() then return end
  printToColor("Returning " .. #sealedTokens .. " tokens to the token pool", playerColor)
  for i = 1, #sealedTokens do
    returnToken(table.remove(sealedTokens))
  end
  updateSave()
  Player[playerColor].clearSelectedObjects()
end

-- returns the token (referenced by GUID) to the chaos bag
---@return boolean: True if a token was returned
function putTokenAway(guid, filterName, silent)
  local token = getObjectFromGUID(guid)
  if not token then return false end

  local name = token.getName()
  if filterName and filterName ~= name then return false end

  local chaosbag = chaosBagApi.findChaosBag()
  chaosbag.putObject(token)

  tokenArrangerApi.layout()

  if name == "Bless" or name == "Curse" then
    blessCurseManagerApi.releasedToken(name, guid, nil, silent)
  end

  return true
end

-- returns the token to the pool (== removes it)
function returnToken(guid)
  local token = getObjectFromGUID(guid)
  if not token then return end

  local name = token.getName()
  token.destruct()
  if name == "Bless" or name == "Curse" then
    blessCurseManagerApi.returnedToken(name, guid)
  end
end

-- resolves sealed token as if it came from the chaos bag
function resolveSealed(playerColor)
  self.removeFromPlayerSelection(playerColor)
  if #sealedTokens == 0 then
    broadcastToAll("No tokens sealed.", "Red")
    return
  end

  -- make list of token names
  local tokenNames = {}
  local differentNames = 0
  for _, guid in ipairs(sealedTokens) do
    local token = getObjectFromGUID(guid)
    if token ~= nil then
      local name = token.getName()
      if tokenNames[name] == nil then
        differentNames = differentNames + 1
      end
      tokenNames[name] = guid
    end
  end

  -- if there are multiple tokens, ask the player to choose
  if differentNames < 2 then
    resolveTokenByGuid(playerColor, table.remove(sealedTokens))
    updateSave()
  else
    local choices = {}
    for name, _ in pairs(tokenNames) do
      table.insert(choices, name)
    end
    Player[playerColor].showOptionsDialog("Choose token to resolve:", choices, 1, function(optionText, optionIndex)
      for i = #sealedTokens, 1, -1 do
        local token = getObjectFromGUID(sealedTokens[i])
        if token ~= nil and token.getName() == optionText then
          resolveTokenByGuid(playerColor, table.remove(sealedTokens, i))
          updateSave()
          return
        end
      end
    end)
  end
end

function resolveTokenByGuid(playerColor, guidToBeResolved)
  local resolvedToken = getObjectFromGUID(guidToBeResolved)
  if resolvedToken ~= nil then
    resolvedToken.UI.setXml("")
  end

  local closestMatColor = playermatApi.getMatColorByPosition(self.getPosition())
  chaosBagApi.drawChaosToken(closestMatColor, true, _, guidToBeResolved)
  Player[playerColor].clearSelectedObjects()
end

function updateStackSize()
  if MAX_SEALED == 1 then return end
  if #sealedTokens == 0 then return end

  -- get topmost sealed token
  local topToken = getObjectFromGUID(sealedTokens[#sealedTokens])
  if topToken == nil then return end

  -- handling for two-digit numbers
  local fontsize = 380
  if #sealedTokens > 9 then
    fontsize = 360
  end

  topToken.UI.setXmlTable({
    {
      tag = "Panel",
      attributes = {
        height = 380,
        width = 380,
        rotation = "0 0 180",
        scale = "0.2 0.2 1",
        position = "0 0 -12",
        color = tokenColor[topToken.getName()] or "#77674DE6"
      },
      children = {
        tag = "Text",
        attributes = {
          fontSize = fontsize,
          font = "font_teutonic-arkham",
          color = "#ffffff",
          outline = "#000000",
          outlineSize = "8 -8",
          text = "x" .. #sealedTokens
        }
      }
    }
  })
end
end)
__bundle_register("playercards/cards/SealTemplate", function(require, _LOADED, __bundle_register, __bundle_modules)
-- VALID_TOKENS_PLACEHOLDER --

-- INVALID_TOKENS_PLACEHOLDER --

-- UPDATE_ON_HOVER_PLACEHOLDER --

-- MAX_SEALED_PLACEHOLDER --

-- RESOLVE_TOKEN config
-- RESOLVE_TOKEN_PLACEHOLDER --

require("playercards/CardsThatSealTokens")
end)
__bundle_register("playermat/PlayermatApi", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local PlayermatApi = {}
  local guidReferenceApi = require("core/GUIDReferenceApi")
  local searchLib = require("util/SearchLib")
  local localInvestigatorPosition = { x = -1.17, y = 1, z = -0.01 }

  -- Convenience function to look up a mat's object by color, or get all mats.
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@return table: Single-element if only single playermat is requested
  local function getMatForColor(matColor)
    if matColor == "All" then
      return guidReferenceApi.getObjectsByType("Playermat")
    else
      return { matColor = guidReferenceApi.getObjectByOwnerAndType(matColor, "Playermat") }
    end
  end

  -- Returns the color of the closest playermat
  ---@param startPos table Starting position to get the closest mat from
  PlayermatApi.getMatColorByPosition = function(startPos)
    local result, smallestDistance
    for matColor, mat in pairs(getMatForColor("All")) do
      local distance = Vector.between(startPos, mat.getPosition()):magnitude()
      if smallestDistance == nil or distance < smallestDistance then
        smallestDistance = distance
        result = matColor
      end
    end
    return result
  end

  -- Returns the color of the player's hand that is seated next to the playermat
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.getPlayerColor = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.getVar("playerColor")
    end
  end

  -- Returns the color of the playermat that owns the playercolor's hand
  ---@param handColor string Color of the playermat
  PlayermatApi.getMatColor = function(handColor)
    for matColor, mat in pairs(getMatForColor("All")) do
      local playerColor = mat.getVar("playerColor")
      if playerColor == handColor then
        return matColor
      end
    end
    return nil
  end

  -- gets the slot data for the playermat
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.getSlotData = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.getTable("slotData")
    end
  end

  -- sets the slot data for the playermat
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  ---@param newSlotData table New slot data for the playermat
  PlayermatApi.loadSlotData = function(matColor, newSlotData)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.setTable("slotData", newSlotData)
      mat.call("updateSave")
      mat.call("updateSlotSymbols")
      return
    end
  end

  -- Performs a search of the deck area of the requested playermat and returns the result as table
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.getDeckAreaObjects = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.call("getDeckAreaObjects")
    end
  end

  -- Flips the top card of the deck (useful after deck manipulation for Norman Withers)
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.flipTopCardFromDeck = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.call("flipTopCardFromDeck")
    end
  end

  -- Returns the position of the discard pile of the requested playermat
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.getDiscardPosition = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.call("returnGlobalDiscardPosition")
    end
  end

  -- Returns the position of the draw pile of the requested playermat
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.getDrawPosition = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.call("returnGlobalDrawPosition")
    end
  end

  -- Transforms a local position into a global position
  ---@param localPos table Local position to be transformed
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.transformLocalPosition = function(localPos, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.positionToWorld(localPos)
    end
  end

  -- Returns the rotation of the requested playermat
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.returnRotation = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.getRotation()
    end
  end

  -- Returns a table with spawn data (position and rotation) for a helper object
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param helperName string Name of the helper object
  PlayermatApi.getHelperSpawnData = function(matColor, helperName)
    local resultTable = {}
    local localPositionTable = {
      ["Hand Helper"] = Vector(-0.055, 0, -1.132),
      ["Search Assistant"] = Vector(-0.34, 0, -1.132)
    }

    for color, mat in pairs(getMatForColor(matColor)) do
      resultTable[color] = {
        position = mat.positionToWorld(localPositionTable[helperName]),
        rotation = mat.getRotation()
      }
    end
    return resultTable
  end


  -- Triggers the Upkeep for the requested playermat
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param playerColor string Color of the calling player (for messages)
  PlayermatApi.doUpkeepFromHotkey = function(matColor, playerColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("doUpkeepFromHotkey", playerColor)
    end
  end

  -- Handles discarding for the requested playermat for the provided list of objects
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  ---@param objList table List of objects to discard
  PlayermatApi.discardListOfObjects = function(matColor, objList)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("discardListOfObjects", objList)
    end
  end

  -- Gets data about the active investigator
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.getActiveInvestigatorData = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.call("getActiveInvestigatorData")
    end
  end

  -- Gets data about the active investigator
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param newData table New active investigator data (class and id)
  PlayermatApi.setActiveInvestigatorData = function(matColor, newData)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("setActiveInvestigatorData", newData)
    end
  end

  -- Returns the position for encounter card drawing
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  ---@param stack boolean If true, returns the leftmost position instead of the first empty from the right
  PlayermatApi.getEncounterCardDrawPosition = function(matColor, stack)
    for _, mat in pairs(getMatForColor(matColor)) do
      return Vector(mat.call("getEncounterCardDrawPosition", stack))
    end
  end

  -- Sets the requested playermat's snap points to limit snapping to matching card types or not.  If
  -- matchTypes is true, the main card slot snap points will only snap assets, while the
  -- investigator area point will only snap Investigators.  If matchTypes is false, snap points will
  -- be reset to snap all cards.
  ---@param matchCardTypes boolean Whether snap points should only snap for the matching card types
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.setLimitSnapsByType = function(matchCardTypes, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("setLimitSnapsByType", matchCardTypes)
    end
  end

  -- Sets the requested playermat's draw 1 button to visible
  ---@param isDrawButtonVisible boolean Whether the draw 1 button should be visible or not
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.showDrawButton = function(isDrawButtonVisible, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("showDrawButton", isDrawButtonVisible)
    end
  end

  -- Shows or hides the clickable clue counter for the requested playermat
  ---@param showCounter boolean Whether the clickable counter should be present or not
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.clickableClues = function(showCounter, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("clickableClues", showCounter)
    end
  end

  -- Toggles the use of class textures for the requested playermat
  ---@param state boolean Whether the class texture should be used or not
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.useClassTexture = function(state, matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("useClassTexture", state)
    end
  end

  -- updates the texture of the playermat
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param overrideName? string Force a specific texture
  PlayermatApi.updateTexture = function(matColor, overrideName)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("updateTexture", overrideName)
    end
  end

  -- Removes all clues (to the trash for tokens and counters set to 0) for the requested playermat
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.removeClues = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("removeClues")
    end
  end

  -- Reports the clue count for the requested playermat
  ---@param useClickableCounters boolean Controls which type of counter is getting checked
  PlayermatApi.getClueCount = function(useClickableCounters, matColor)
    local count = 0
    for _, mat in pairs(getMatForColor(matColor)) do
      count = count + mat.call("getClueCount", useClickableCounters)
    end
    return count
  end

  -- Updates the specified owned counter
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param type string Counter to target
  ---@param newValue number Value to set the counter to
  ---@param modifier number If newValue is not provided, the existing value will be adjusted by this modifier
  PlayermatApi.updateCounter = function(matColor, type, newValue, modifier)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("updateCounter", { type = type, newValue = newValue, modifier = modifier })
    end
  end

  -- Triggers the draw function for the specified playermat
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param number number Amount of cards to draw
  PlayermatApi.drawCardsWithReshuffle = function(matColor, number)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("drawCardsWithReshuffle", number)
    end
  end

  -- Returns the resource counter amount
  ---@param matColor string Color of the playermat - White, Orange, Green or Red (does not support "All")
  ---@param type string Counter to target
  PlayermatApi.getCounterValue = function(matColor, type)
    for _, mat in pairs(getMatForColor(matColor)) do
      return mat.call("getCounterValue", type)
    end
  end

  -- Returns a list of mat colors that have an investigator placed
  PlayermatApi.getUsedMatColors = function()
    local usedColors = {}
    for matColor, mat in pairs(getMatForColor("All")) do
      local searchPos = mat.positionToWorld(localInvestigatorPosition)
      local searchResult = searchLib.atPosition(searchPos, "isCardOrDeck")
      if #searchResult > 0 then
        table.insert(usedColors, matColor)
      end
    end
    return usedColors
  end

  -- Returns a list of investigator card objects
  PlayermatApi.getUsedInvestigatorCards = function()
    local usedCards = {}
    for matColor, mat in pairs(getMatForColor("All")) do
      local searchPos = mat.positionToWorld(localInvestigatorPosition)
      local searchResult = searchLib.atPosition(searchPos, "isCardOrDeck")
      if #searchResult > 0 then
        usedCards[matColor] = searchResult[1]
      end
    end
    return usedCards
  end

  -- Returns investigator name
  ---@param matColor string Color of the playmat - White, Orange, Green or Red (does not support "All")
  PlayermatApi.getInvestigatorName = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      local searchPos = mat.positionToWorld(localInvestigatorPosition)
      local searchResult = searchLib.atPosition(searchPos, "isCardOrDeck")
      if #searchResult == 1 then
        return searchResult[1].getName()
      end
    end
    return ""
  end

  -- Resets the specified skill tracker to "1, 1, 1, 1"
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.resetSkillTracker = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("resetSkillTracker")
    end
  end

  -- Updates the XML for the slot symbols based on the slotData table
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.updateSlotSymbols = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("updateSlotSymbols")
    end
  end

  -- Finds all objects on the playermat and associated set aside zone and returns a table
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param filter? string Name of the filte function (see util/SearchLib)
  PlayermatApi.searchAroundPlayermat = function(matColor, filter)
    local objList = {}
    for _, mat in pairs(getMatForColor(matColor)) do
      for _, obj in ipairs(mat.call("searchAroundSelf", filter)) do
        table.insert(objList, obj)
      end
    end
    return objList
  end

  -- Discard a non-hidden card from the corresponding player's hand
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.doDiscardOne = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("doDiscardOne")
    end
  end

  -- Spawns the regular action tokens
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  PlayermatApi.spawnActionTokens = function(matColor)
    for _, mat in pairs(getMatForColor(matColor)) do
      mat.call("spawnActionTokens")
    end
  end

  -- Triggers the metadata sync for all playermats
  PlayermatApi.syncAllCustomizableCards = function()
    for _, mat in pairs(getMatForColor("All")) do
      mat.call("syncAllCustomizableCards")
    end
  end

  -- moves + rotates a playermat (and related objects)
  ---@param matColor string Color of the playermat - White, Orange, Green, Red or All
  ---@param position? table New position for the playermat
  ---@param rotationY? number New y-rotation for the playermat (X and Z will be 0)
  ---@param positionOffset? table Positional offset for the playermat
  PlayermatApi.moveAndRotate = function(matColor, position, rotationY, positionOffset)
    -- get mat and related objects
    local mat = guidReferenceApi.getObjectByOwnerAndType(matColor, "Playermat")
    if not mat then return end

    -- get current transform data
    local currentMatPos = mat.getPosition()
    local currentMatRotY = mat.getRotation().y

    -- use current values if undefined
    position = position or currentMatPos
    rotationY = rotationY or currentMatRotY

    if positionOffset then
      position = Vector(position) + Vector(positionOffset)
    end

    local movedObjects = {}
    local function moveAndRotateObject(obj)
      local relativePos = obj.getPosition() - currentMatPos
      obj.setPosition(position + relativePos:rotateOver("y", rotationY - currentMatRotY))

      if obj.type == "Hand" then
        obj.setRotation({ 0, rotationY + 180, 0 })
      else
        local objRot = obj.getRotation()
        local relativeRotY = objRot.y - currentMatRotY
        obj.setRotation({ objRot.x, rotationY + relativeRotY, objRot.z })
      end

      movedObjects[obj.getGUID()] = true
    end

    -- get objects on the mat
    for _, obj in ipairs(searchLib.onObject(mat, "isInteractable")) do
      if not movedObjects[obj.getGUID()] then
        -- make sure object isn't owned by another mat
        local owner = guidReferenceApi.getOwnerOfObject(obj)
        if owner == "Mythos" or owner == matColor then
          moveAndRotateObject(obj)
        end
      end
    end

    -- move owned objects (including the mat)
    for _, obj in pairs(guidReferenceApi.getObjectsByOwner(matColor)) do
      if not movedObjects[obj.getGUID()] then
        moveAndRotateObject(obj)
      end
    end
  end

  return PlayermatApi
end
end)
__bundle_register("tokens/TokenArrangerApi", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local TokenArrangerApi = {}
  local guidReferenceApi = require("core/GUIDReferenceApi")

  -- internal function to create a copy of the table to avoid operating on variables owned by different objects
  local function deepCopy(data)
    if type(data) ~= "table" then return data end
    local copiedList = {}
    for key, value in pairs(data) do
      if type(value) == "table" then
        copiedList[key] = deepCopy(value)
      else
        copiedList[key] = value
      end
    end
    return copiedList
  end

  -- local function to call the token arranger, if it is on the table
  ---@param functionName string Name of the function to cal
  ---@param argument? table Parameter to pass
  local function callIfExistent(functionName, argument)
    local tokenArranger = guidReferenceApi.getObjectByOwnerAndType("Mythos", "TokenArranger")
    if tokenArranger ~= nil then
      return tokenArranger.call(functionName, argument)
    end
  end

  -- updates the token modifiers with the provided data
  ---@param fullData table Contains the chaos token metadata
  TokenArrangerApi.onTokenDataChanged = function(fullData)
    callIfExistent("onTokenDataChanged", fullData)
  end

  -- deletes already laid out tokens
  TokenArrangerApi.deleteCopiedTokens = function()
    callIfExistent("deleteCopiedTokens")
  end

  -- updates the laid out tokens
  TokenArrangerApi.layout = function()
    Wait.time(function() callIfExistent("layout") end, 0.1)
  end

  TokenArrangerApi.getSaveData = function()
    return deepCopy(callIfExistent("getSaveData"))
  end

  TokenArrangerApi.loadData = function(loadedData)
    callIfExistent("loadData", loadedData)
  end

  return TokenArrangerApi
end
end)
__bundle_register("util/SearchLib", function(require, _LOADED, __bundle_register, __bundle_modules)
do
  local SearchLib = {}
  local filterFunctions = {
    isCard = function(x) return x.type == "Card" end,
    isDeck = function(x) return x.type == "Deck" end,
    isCardOrDeck = function(x) return x.type == "Card" or x.type == "Deck" end,
    isClue = function(x) return x.memo == "clueDoom" and x.is_face_down == false end,
    isDoom = function(x) return x.memo == "clueDoom" and x.is_face_down == true end,
    isInteractable = function(x) return x.interactable end,
    isTileOrToken = function(x) return not x.Book and (x.type == "Tile" or x.type == "Generic") end,
    isUniversalToken = function(x) return x.getMemo() == "universalActionAbility" end,
  }

  -- performs the actual search and returns a filtered list of object references
  ---@param pos tts__Vector Global position
  ---@param rot? tts__Vector Global rotation
  ---@param size table Size
  ---@param filter? string Name of the filter function
  ---@param direction? table Direction (positive is up)
  ---@param maxDistance? number Distance for the cast
  local function returnSearchResult(pos, rot, size, filter, direction, maxDistance)
    local filterFunc = filter and filterFunctions[filter]
    local searchResult = Physics.cast({
      origin       = pos,
      direction    = direction or { 0, 1, 0 },
      orientation  = rot or { 0, 0, 0 },
      type         = 3,
      size         = size,
      max_distance = maxDistance or 0
    })

    -- filter the result for matching objects
    local objList = {}
    for _, v in ipairs(searchResult) do
      if (not filter or filterFunc(v.hit_object)) then
        table.insert(objList, v.hit_object)
      end
    end
    return objList
  end

  -- searches the specified area
  function SearchLib.inArea(pos, rot, size, filter)
    return returnSearchResult(pos, rot, size, filter)
  end

  -- searches the area on an object
  function SearchLib.onObject(obj, filter, scale)
    scale = scale or 1
    local pos = obj.getPosition() + Vector(0, 1, 0) -- offset by half the cast's height
    local size = obj.getBounds().size:scale(scale):setAt("y", 2)
    return returnSearchResult(pos, _, size, filter)
  end

  -- searches the area directly below an object
  function SearchLib.belowObject(obj, filter, scale)
    scale = scale or 1
    local pos = obj.getPosition() + Vector(0, -1, 0) -- offset by half the cast's height
    local size = obj.getBounds().size:scale(scale):setAt("y", 2)
    return returnSearchResult(pos, _, size, filter)
  end

  -- searches the specified position (a single point)
  function SearchLib.atPosition(pos, filter)
    local size = { 0.1, 2, 0.1 }
    return returnSearchResult(pos, _, size, filter)
  end

  -- searches below the specified position (downwards until y = 0)
  function SearchLib.belowPosition(pos, filter)
    local size = { 0.1, 2, 0.1 }
    local direction = { 0, -1, 0 }
    local maxDistance = pos.y
    return returnSearchResult(pos, _, size, filter, direction, maxDistance)
  end

  return SearchLib
end
end)
return __bundle_require("__root")
