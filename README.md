# Procedural Asset Generation API

A REST API for generating retro-style pixel art sprites and sound effects procedurally. Built with FastAPI, Pillow, and NumPy.

## Features

- **Sprite Generation**: Create pixel art sprites for players, enemies, projectiles, items, and effects
- **Sound Generation**: Synthesize retro arcade-style sound effects and UI sounds
- **Seed-based**: Use seeds for reproducible generation
- **Color Customization**: Apply custom color palettes or use style presets
- **Batch Generation**: Generate multiple assets in a single request
- **Fast**: Built with FastAPI for high performance
- **Easy to Deploy**: Simple Python application

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

Start the server:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

For production, use uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Endpoints

### Generate Sprite

**POST** `/generate/sprite`

Request body:
```json
{
  "type": "player",
  "seed": 12345,
  "size": 64,
  "style": "neon",
  "primary_color": "#FF006E",
  "secondary_color": "#8338EC",
  "accent_color": "#3A86FF"
}
```

**Available sprite types (29 total):**
- **Ships**: `player`
- **Enemies**: `enemy_grunt`, `enemy_drone`, `enemy_turret`, `enemy_carrier`, `enemy_flanker`, `enemy_kamikaze`, `enemy_bomber`, `enemy_weaver`
- **Aliens**: `alien_grunt`, `alien_drone`
- **Mechs**: `mech_grunt`, `mech_drone`
- **Swarm**: `swarm_enemy`
- **Bosses**: `boss_core`, `boss_gun`, `boss_alien`, `boss_mech`
- **Projectiles**: `vulcan_bullet`, `laser_bolt`, `spread_bullet`, `missile`, `enemy_bullet`
- **Items**: `power_up`, `bomb`
- **Effects**: `explosion_sheet`, `spark_sheet`
- **Backgrounds**: `background_stars`

**Style presets**: `retro`, `neon`, `monochrome`, `cyberpunk`, `forest`, `ocean`, `sunset`

Returns: PNG image

### Generate Sound

**POST** `/generate/sound`

Request body:
```json
{
  "type": "vulcan",
  "seed": 12345
}
```

**Available sound types (13 total):**
- **Weapons**: `vulcan`, `laser`, `spread`, `missile`
- **Explosions**: `explosion_small`, `explosion_medium`, `explosion_large`
- **Player**: `player_death`
- **UI**: `ui_click`, `ui_hover`, `ui_confirm`, `ui_cancel`
- **Items**: `powerup`

Returns: WAV audio file

### Batch Generate Sprites

**POST** `/generate/sprites/batch`

Request body:
```json
{
  "types": ["player", "enemy_grunt", "enemy_drone"],
  "seed": 12345,
  "size": 64,
  "style": "neon"
}
```

Returns: ZIP file containing all requested sprites as PNG files

### Batch Generate Sounds

**POST** `/generate/sounds/batch`

Request body:
```json
{
  "types": ["vulcan", "laser", "explosion_small"],
  "seed": 12345
}
```

Returns: ZIP file containing all requested sounds as WAV files

### List Available Types

**GET** `/sprites/types` - List available sprite types with categories

**GET** `/sounds/types` - List available sound types with categories

**GET** `/styles/presets` - List available style presets with color palettes

## Color Customization

You can customize sprite colors in three ways:

1. **Style Presets**: Use predefined color schemes
   ```json
   {"type": "player", "style": "neon"}
   ```

2. **Custom Colors**: Specify hex colors for different luminance ranges
   ```json
   {
     "type": "player",
     "primary_color": "#FF006E",
     "secondary_color": "#8338EC",
     "accent_color": "#3A86FF"
   }
   ```

3. **Combined**: Use preset as base, override specific colors
   ```json
   {
     "type": "player",
     "style": "neon",
     "accent_color": "#FFD700"
   }
   ```

**How it works:**
- `primary_color`: Applied to dark areas (luminance < 0.4)
- `secondary_color`: Applied to mid-tones (0.4 < luminance < 0.7)
- `accent_color`: Applied to bright areas (luminance > 0.7)

## Example Usage

### Python (requests)

```python
import requests

# Generate a sprite with custom colors
response = requests.post('http://localhost:8000/generate/sprite', json={
    'type': 'player',
    'seed': 12345,
    'size': 64,
    'style': 'neon'
})

with open('player.png', 'wb') as f:
    f.write(response.content)

# Generate a sound
response = requests.post('http://localhost:8000/generate/sound', json={
    'type': 'vulcan',
    'seed': 12345
})

with open('vulcan.wav', 'wb') as f:
    f.write(response.content)

# Batch generate sprites
response = requests.post('http://localhost:8000/generate/sprites/batch', json={
    'types': ['player', 'enemy_grunt', 'enemy_drone'],
    'seed': 12345,
    'style': 'cyberpunk'
})

with open('sprites.zip', 'wb') as f:
    f.write(response.content)
```

### cURL

```bash
# Generate sprite with style preset
curl -X POST http://localhost:8000/generate/sprite \
  -H "Content-Type: application/json" \
  -d '{"type": "player", "seed": 12345, "style": "neon"}' \
  --output player.png

# Generate sprite with custom colors
curl -X POST http://localhost:8000/generate/sprite \
  -H "Content-Type: application/json" \
  -d '{"type": "player", "seed": 12345, "primary_color": "#FF006E", "secondary_color": "#8338EC", "accent_color": "#3A86FF"}' \
  --output player_custom.png

# Generate sound
curl -X POST http://localhost:8000/generate/sound \
  -H "Content-Type: application/json" \
  -d '{"type": "vulcan", "seed": 12345}' \
  --output vulcan.wav

# Batch generate sprites
curl -X POST http://localhost:8000/generate/sprites/batch \
  -H "Content-Type: application/json" \
  -d '{"types": ["player", "enemy_grunt", "enemy_drone"], "seed": 12345, "style": "retro"}' \
  --output sprites.zip
```

## Deployment

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t procedural-gen-api .
docker run -p 8000:8000 procedural-gen-api
```

### Railway/Render/Fly.io

These platforms support Python apps directly. Just push this repository and configure:
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Adding More Generators

To add new sprite or sound types:

1. Add generation methods to `sprite_generator.py` or `sound_generator.py`
2. Add the new type to the appropriate endpoint in `main.py`
3. Update the type lists in the `/types` endpoints

## License

MIT

## Credits

Based on the procedural generation algorithms from Vortex Vanguard game.
