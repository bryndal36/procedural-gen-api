# Comprehensive API Test Script
# Run this after starting the server with: python main.py

Write-Host "=== Procedural Generation API - Comprehensive Test ===" -ForegroundColor Green
Write-Host ""

# Test root endpoint
Write-Host "Testing root endpoint..." -ForegroundColor Cyan
Invoke-RestMethod -Uri http://localhost:8000/ -Method GET | Format-List

# Test sprite types endpoint
Write-Host "`nTesting sprite types endpoint..." -ForegroundColor Cyan
Invoke-RestMethod -Uri http://localhost:8000/sprites/types -Method GET | Format-List

# Test sound types endpoint
Write-Host "`nTesting sound types endpoint..." -ForegroundColor Cyan
Invoke-RestMethod -Uri http://localhost:8000/sounds/types -Method GET | Format-List

Write-Host "`n=== Testing Sprite Generation ===" -ForegroundColor Green

# Test all enemy sprites
$enemies = @("enemy_grunt", "enemy_drone", "enemy_turret", "enemy_carrier", 
             "enemy_flanker", "enemy_kamikaze", "enemy_bomber", "enemy_weaver")

foreach ($enemy in $enemies) {
    Write-Host "Generating $enemy..." -ForegroundColor Yellow
    $body = @{type=$enemy; seed=12345} | ConvertTo-Json
    Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "$enemy.png"
    Write-Host "  Saved: $enemy.png" -ForegroundColor Green
}

# Test boss sprites
Write-Host "`nGenerating boss sprites..." -ForegroundColor Yellow
$body = @{type="boss_core"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "boss_core.png"
Write-Host "  Saved: boss_core.png" -ForegroundColor Green

$body = @{type="boss_gun"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "boss_gun.png"
Write-Host "  Saved: boss_gun.png" -ForegroundColor Green

# Test projectiles
Write-Host "`nGenerating projectile sprites..." -ForegroundColor Yellow
$projectiles = @("vulcan_bullet", "laser_bolt", "spread_bullet", "missile", "enemy_bullet")

foreach ($proj in $projectiles) {
    $body = @{type=$proj; seed=12345} | ConvertTo-Json
    Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "$proj.png"
    Write-Host "  Saved: $proj.png" -ForegroundColor Green
}

# Test items and effects
Write-Host "`nGenerating items and effects..." -ForegroundColor Yellow
$body = @{type="power_up"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "power_up.png"
Write-Host "  Saved: power_up.png" -ForegroundColor Green

$body = @{type="bomb"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "bomb.png"
Write-Host "  Saved: bomb.png" -ForegroundColor Green

$body = @{type="explosion_sheet"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "explosion_sheet.png"
Write-Host "  Saved: explosion_sheet.png" -ForegroundColor Green

$body = @{type="spark_sheet"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "spark_sheet.png"
Write-Host "  Saved: spark_sheet.png" -ForegroundColor Green

# Test background
Write-Host "`nGenerating background..." -ForegroundColor Yellow
$body = @{type="background_stars"; seed=42} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile "background_stars.png"
Write-Host "  Saved: background_stars.png" -ForegroundColor Green

Write-Host "`n=== Testing Sound Generation ===" -ForegroundColor Green

# Test all sound types
$sounds = @("vulcan", "laser", "spread", "missile", 
            "explosion_small", "explosion_medium", "explosion_large", "player_death")

foreach ($sound in $sounds) {
    Write-Host "Generating $sound sound..." -ForegroundColor Yellow
    $body = @{type=$sound; seed=12345} | ConvertTo-Json
    Invoke-RestMethod -Uri http://localhost:8000/generate/sound -Method POST -Body $body -ContentType "application/json" -OutFile "$sound.wav"
    Write-Host "  Saved: $sound.wav" -ForegroundColor Green
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "All assets have been generated and saved to the current directory." -ForegroundColor Cyan
Write-Host "Check the generated PNG and WAV files to verify the API is working correctly." -ForegroundColor Cyan
