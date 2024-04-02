$FilePath = "C:\Users\vikit\OneDrive\Рабочий стол\window_position.txt"

# Проверяем наличие второго монитора
Add-Type -AssemblyName System.Windows.Forms
$SecondScreen = [System.Windows.Forms.Screen]::AllScreens | Where-Object {$_.DeviceName -like "*\\.\DISPLAY2*"}
Write-Host $SecondScreen

# Устанавливаем ширину и высоту экрана второго монитора
$Width = $SecondScreen.Bounds.Width
$Height = $SecondScreen.Bounds.Height

# Проверяем наличие файла
if (Test-Path $FilePath) {
    # Читаем координаты из файла
    $PositionData = Get-Content $FilePath -Raw | ConvertFrom-Json
    $X = $PositionData.x
    $Y = $PositionData.y

    # Если второй монитор найден, используем координаты из файла
    if ($SecondScreen) {
        $PositionArgs = "--monitor 2 --position $X,$Y,$Width,$Height"
    }
    else {
        # Если второй монитор не найден, используем аргумент --min
        $PositionArgs = "--monitor 2 --position $X,$Y,$Width,$Height --min"
    }
}
else {
    # Если второй монитор найден, используем его размеры
    if ($SecondScreen) {
        $X = $SecondScreen.Bounds.Left
        $Y = $SecondScreen.Bounds.Top

        $PositionData = @{
            x = $X
            y = $Y
        }
        $PositionData | ConvertTo-Json | Set-Content $FilePath
        $PositionArgs = "--monitor 2 --position $X,$Y,$Width,$Height"
    }
    else {
        # Если нет ни файла ни второго монитора, используем аргументы --monitor 2 --min
        $PositionArgs = "--monitor 2 --min"
    }
}

# Запуск приложения с указанием позиции окна или аргументом --min
$ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
$ProcessInfo.FileName = "C:\Program Files\TrueConf\Room\TrueConfRoom.exe"
$ProcessInfo.Arguments = $PositionArgs
[System.Diagnostics.Process]::Start($ProcessInfo)










