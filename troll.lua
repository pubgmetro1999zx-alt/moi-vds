local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local HttpService = game:GetService("HttpService")
local LocalPlayer = Players.LocalPlayer

-- GUI Setup
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "UniversalTrollGUI_" .. HttpService:GenerateGUID(false)
ScreenGui.Parent = game.CoreGui
ScreenGui.ResetOnSpawn = false
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling

local MainFrame = Instance.new("Frame")
MainFrame.Size = UDim2.new(0, 400, 0, 500)
MainFrame.Position = UDim2.new(0.5, -200, 0.5, -250)
MainFrame.BackgroundColor3 = Color3.fromRGB(15, 15, 25)
MainFrame.BorderSizePixel = 0
MainFrame.ClipsDescendants = true
MainFrame.Active = true
MainFrame.Draggable = true
MainFrame.Parent = ScreenGui

local UICorner = Instance.new("UICorner")
UICorner.CornerRadius = UDim.new(0, 12)
UICorner.Parent = MainFrame

local UIStroke = Instance.new("UIStroke")
UIStroke.Color = Color3.fromRGB(80, 60, 140)
UIStroke.Thickness = 2
UIStroke.Parent = MainFrame

-- Title Bar
local TitleBar = Instance.new("Frame")
TitleBar.Size = UDim2.new(1, 0, 0, 40)
TitleBar.BackgroundColor3 = Color3.fromRGB(25, 20, 45)
TitleBar.BorderSizePixel = 0
TitleBar.Parent = MainFrame

local TitleCorner = Instance.new("UICorner")
TitleCorner.CornerRadius = UDim.new(0, 12)
TitleCorner.Parent = TitleBar

local TitleLabel = Instance.new("TextLabel")
TitleLabel.Size = UDim2.new(0.7, 0, 1, 0)
TitleLabel.Position = UDim2.new(0.05, 0, 0, 0)
TitleLabel.Text = "UNIVERSAL TROLL SYSTEM"
TitleLabel.TextColor3 = Color3.fromRGB(220, 180, 255)
TitleLabel.BackgroundTransparency = 1
TitleLabel.TextScaled = true
TitleLabel.Font = Enum.Font.GothamBold
TitleLabel.Parent = TitleBar

-- Control Buttons
local CloseButton = Instance.new("TextButton")
CloseButton.Size = UDim2.new(0, 30, 0, 30)
CloseButton.Position = UDim2.new(1, -35, 0, 5)
CloseButton.Text = "X"
CloseButton.BackgroundColor3 = Color3.fromRGB(200, 60, 60)
CloseButton.TextColor3 = Color3.white
CloseButton.TextScaled = true
CloseButton.Font = Enum.Font.GothamBold
CloseButton.Parent = TitleBar

local MinimizeButton = Instance.new("TextButton")
MinimizeButton.Size = UDim2.new(0, 30, 0, 30)
MinimizeButton.Position = UDim2.new(1, -70, 0, 5)
MinimizeButton.Text = "_"
MinimizeButton.BackgroundColor3 = Color3.fromRGB(100, 100, 150)
CloseButton.TextColor3 = Color3.white
MinimizeButton.TextScaled = true
MinimizeButton.Font = Enum.Font.GothamBold
MinimizeButton.Parent = TitleBar

-- Content Frame
local ContentFrame = Instance.new("ScrollingFrame")
ContentFrame.Size = UDim2.new(1, -20, 1, -60)
ContentFrame.Position = UDim2.new(0, 10, 0, 50)
ContentFrame.BackgroundTransparency = 1
ContentFrame.ScrollBarThickness = 4
ContentFrame.ScrollBarImageColor3 = Color3.fromRGB(80, 60, 140)
ContentFrame.Parent = MainFrame

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Padding = UDim.new(0, 10)
UIListLayout.Parent = ContentFrame

-- Functions Storage
local TrollFunctions = {
    ServerCrash = false,
    GiantMode = false,
    DDoSAttack = false,
    AntiGravity = false,
    SpeedHack = false,
    NoClip = false,
    ChatSpam = false,
    Invisible = false
}

local Connections = {}

-- Function: Server Crash
local function activateServerCrash()
    TrollFunctions.ServerCrash = true
    spawn(function()
        while TrollFunctions.ServerCrash and task.wait(0.01) do
            pcall(function()
                -- Массовая отправка пакетов
                for i = 1, 50 do
                    game:GetService("ReplicatedStorage"):FindFirstChildOfClass("RemoteEvent"):FireServer()
                    game:GetService("ReplicatedStorage"):FindFirstChildOfClass("RemoteFunction"):InvokeServer()
                end
            end)
        end
    end)
end

-- Function: Giant Mode
local function activateGiantMode()
    TrollFunctions.GiantMode = true
    local function makeGiant(character)
        for _, part in pairs(character:GetDescendants()) do
            if part:IsA("BasePart") then
                part.Size = part.Size * 8
                part.Color = Color3.fromRGB(255, 50, 50)
                part.Material = Enum.Material.Neon
            end
        end
    end
    
    if LocalPlayer.Character then
        makeGiant(LocalPlayer.Character)
    end
    LocalPlayer.CharacterAdded:Connect(makeGiant)
end

-- Function: DDoS Attack
local function activateDDoSAttack()
    TrollFunctions.DDoSAttack = true
    spawn(function()
        while TrollFunctions.DDoSAttack and task.wait() do
            pcall(function()
                -- Интенсивная нагрузка на сервер
                for i = 1, 100 do
                    game:GetService("ReplicatedStorage"):GetChildren()[1]:FireServer()
                end
            end)
        end
    end)
end

-- Function: Anti-Gravity
local function activateAntiGravity()
    TrollFunctions.AntiGravity = true
    spawn(function()
        while TrollFunctions.AntiGravity and task.wait(0.1) do
            pcall(function()
                local char = LocalPlayer.Character
                if char and char:FindFirstChild("HumanoidRootPart") then
                    char.HumanoidRootPart.Velocity = Vector3.new(0, 100, 0)
                end
            end)
        end
    end)
end

-- Function: Speed Hack
local function activateSpeedHack()
    TrollFunctions.SpeedHack = true
    LocalPlayer.CharacterAdded:Connect(function(char)
        task.wait(1)
        if TrollFunctions.SpeedHack and char:FindFirstChild("Humanoid") then
            char.Humanoid.WalkSpeed = 120
        end
    end)
    if LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("Humanoid") then
        LocalPlayer.Character.Humanoid.WalkSpeed = 120
    end
end

-- Function: NoClip
local function activateNoClip()
    TrollFunctions.NoClip = true
    Connections.NoClip = RunService.Stepped:Connect(function()
        if TrollFunctions.NoClip and LocalPlayer.Character then
            for _, part in pairs(LocalPlayer.Character:GetDescendants()) do
                if part:IsA("BasePart") then
                    part.CanCollide = false
                end
            end
        end
    end)
end

-- Function: Chat Spam
local function activateChatSpam()
    TrollFunctions.ChatSpam = true
    spawn(function()
        local messages = {
            "🚀 UNIVERSAL TROLL SYSTEM ACTIVATED!",
            "💥 SERVER WILL CRASH SOON!",
            "🔴 YOU CAN'T STOP ME!",
            "⚡ POWERED BY EXPLOITS!",
            "🌪️ CHAOS MODE: ON!"
        }
        while TrollFunctions.ChatSpam and task.wait(3) do
            pcall(function()
                game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer(
                    messages[math.random(1, #messages)], "All"
                )
            end)
        end
    end)
end

-- Function: Invisible
local function activateInvisible()
    TrollFunctions.Invisible = true
    LocalPlayer.CharacterAdded:Connect(function(char)
        task.wait(1)
        if TrollFunctions.Invisible then
            for _, part in pairs(char:GetDescendants()) do
                if part:IsA("BasePart") then
                    part.Transparency = 1
                end
            end
        end
    end)
    if LocalPlayer.Character then
        for _, part in pairs(LocalPlayer.Character:GetDescendants()) do
            if part:IsA("BasePart") then
                part.Transparency = 1
            end
        end
    end
end

-- Create Toggle Buttons
local function createToggleButton(text, functionName, activateFunc)
    local buttonFrame = Instance.new("Frame")
    buttonFrame.Size = UDim2.new(1, 0, 0, 50)
    buttonFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 40)
    buttonFrame.BorderSizePixel = 0
    buttonFrame.Parent = ContentFrame
    
    local buttonCorner = Instance.new("UICorner")
    buttonCorner.CornerRadius = UDim.new(0, 8)
    buttonCorner.Parent = buttonFrame
    
    local buttonStroke = Instance.new("UIStroke")
    buttonStroke.Color = Color3.fromRGB(60, 45, 100)
    buttonStroke.Parent = buttonFrame
    
    local toggleButton = Instance.new("TextButton")
    toggleButton.Size = UDim2.new(1, -20, 1, -10)
    toggleButton.Position = UDim2.new(0, 10, 0, 5)
    toggleButton.Text = text
    toggleButton.BackgroundColor3 = Color3.fromRGB(80, 60, 140)
    toggleButton.TextColor3 = Color3.white
    toggleButton.TextScaled = true
    toggleButton.Font = Enum.Font.Gotham
    toggleButton.Parent = buttonFrame
    
    local toggleCorner = Instance.new("UICorner")
    toggleCorner.CornerRadius = UDim.new(0, 6)
    toggleCorner.Parent = toggleButton
    
    toggleButton.MouseButton1Click:Connect(function()
        TrollFunctions[functionName] = not TrollFunctions[functionName]
        
        if TrollFunctions[functionName] then
            toggleButton.BackgroundColor3 = Color3.fromRGB(60, 180, 80)
            activateFunc()
        else
            toggleButton.BackgroundColor3 = Color3.fromRGB(80, 60, 140)
            -- Отключаем соединения если есть
            if Connections[functionName] then
                Connections[functionName]:Disconnect()
            end
        end
    end)
end

-- Create all toggle buttons
createToggleButton("💥 SERVER CRASH MODE", "ServerCrash", activateServerCrash)
createToggleButton("🦍 GIANT CHARACTER MODE", "GiantMode", activateGiantMode)
createToggleButton("🌪️ DDoS SERVER ATTACK", "DDoSAttack", activateDDoSAttack)
createToggleButton("🚀 ANTI-GRAVITY MODE", "AntiGravity", activateAntiGravity)
createToggleButton("⚡ SUPER SPEED HACK", "SpeedHack", activateSpeedHack)
createToggleButton("👻 NO CLIP MODE", "NoClip", activateNoClip)
createToggleButton("💬 CHAT SPAM BOT", "ChatSpam", activateChatSpam)
createToggleButton("🔮 INVISIBLE MODE", "Invisible", activateInvisible)

-- GUI Controls
CloseButton.MouseButton1Click:Connect(function()
    ScreenGui:Destroy()
end)

MinimizeButton.MouseButton1Click:Connect(function()
    ContentFrame.Visible = not ContentFrame.Visible
    if ContentFrame.Visible then
        MainFrame.Size = UDim2.new(0, 400, 0, 500)
    else
        MainFrame.Size = UDim2.new(0, 400, 0, 40)
    end
end)

-- Hotkey to toggle GUI
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if not gameProcessed and input.KeyCode == Enum.KeyCode.RightControl then
        MainFrame.Visible = not MainFrame.Visible
    end
end)

print("🎮 UNIVERSAL TROLL SYSTEM LOADED!")
print("📝 Hotkey: RightControl - Toggle GUI")
print("⚠️  Use at your own risk!")
