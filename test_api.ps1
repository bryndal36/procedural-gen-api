# Procedural Generation API - PowerShell Test Commands

# Start the server first:
# python main.py

# Test the root endpoint
Invoke-RestMethod -Uri http://localhost:8000/ -Method GET

# Generate a player sprite
$body = @{type="player"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile player.png
Write-Host "Player sprite saved to player.png"

# Generate an enemy grunt sprite
$body = @{type="enemy_grunt"; seed=99999} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sprite -Method POST -Body $body -ContentType "application/json" -OutFile grunt.png
Write-Host "Grunt sprite saved to grunt.png"

# Generate a vulcan sound
$body = @{type="vulcan"; seed=12345} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sound -Method POST -Body $body -ContentType "application/json" -OutFile vulcan.wav
Write-Host "Vulcan sound saved to vulcan.wav"

# Generate an explosion sound
$body = @{type="explosion_large"; seed=54321} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/generate/sound -Method POST -Body $body -ContentType "application/json" -OutFile explosion.wav
Write-Host "Explosion sound saved to explosion.wav"

# List available sprite types
Invoke-RestMethod -Uri http://localhost:8000/sprites/types -Method GET

# List available sound types
Invoke-RestMethod -Uri http://localhost:8000/sounds/types -Method GET
